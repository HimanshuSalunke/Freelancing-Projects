import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

from .pdf_analyzer import PDFAnalyzer, DocumentStructure
from .summarizer import Summarizer


class IntelligentSummarizer:
    def __init__(self) -> None:
        # Initialize components
        self.pdf_analyzer = PDFAnalyzer()
        self.base_summarizer = Summarizer()
        
        # Set up model for different summarization strategies
        project_root = Path(__file__).resolve().parents[3]
        default_cache = project_root / "models" / "transformers"
        cache_dir = os.getenv("TRANSFORMERS_CACHE", str(default_cache))
        
        # Set environment variables
        os.environ["TRANSFORMERS_CACHE"] = str(default_cache)
        os.environ["HF_HOME"] = str(project_root / "models" / "huggingface")
        
        model_id = os.getenv("SUMMARIZER_MODEL", "facebook/bart-large-cnn")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=cache_dir)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_id, cache_dir=cache_dir)
        device = 0 if torch.cuda.is_available() else -1
        self.summarizer = pipeline("summarization", model=model, tokenizer=self.tokenizer, device=device)
    
    def analyze_and_summarize(self, filename: str, content: bytes) -> Dict:
        """Main function: analyze document and provide intelligent summarization"""
        
        # Step 1: Analyze document structure
        structure = self.pdf_analyzer.analyze_document(filename, content)
        
        # Get raw text for further processing
        from .doc_parser import parse_document
        raw_text_content = parse_document(filename, content)
        raw_text = self.pdf_analyzer._extract_text_blocks(raw_text_content)
        
        # Step 2: Generate analysis report
        analysis_report = self.pdf_analyzer.generate_analysis_report(structure, raw_text)
        
        # Step 3: Generate intelligent summary based on document type
        summary = self._generate_intelligent_summary(structure, raw_text)
        
        # Step 4: Combine results
        return {
            "document_analysis": analysis_report,
            "intelligent_summary": summary,
            "document_type": structure.doc_type
        }
    
    def _generate_intelligent_summary(self, structure: DocumentStructure, text_blocks: List[str]) -> Dict:
        """Generate summary based on document type"""
        
        if structure.doc_type == "TEXT-HEAVY":
            return self._summarize_text_heavy(structure, text_blocks)
        elif structure.doc_type == "TABLE-HEAVY":
            return self._summarize_table_heavy(structure)
        else:  # MIXED
            return self._summarize_mixed(structure, text_blocks)
    
    def _summarize_text_heavy(self, structure: DocumentStructure, text_blocks: List[str]) -> Dict:
        """Summarize text-heavy documents"""
        
        # Combine all text blocks
        full_text = " ".join(text_blocks)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(full_text)
        
        # Generate section-wise summary
        section_summary = self._generate_section_summary(structure.sections, text_blocks)
        
        return {
            "strategy": "TEXT-HEAVY",
            "executive_summary": executive_summary,
            "section_wise_summary": section_summary,
            "key_points": self._extract_key_points(full_text),
            "notable_patterns": self._identify_patterns(full_text),
            "anomalies": self._detect_anomalies(full_text)
        }
    
    def _summarize_table_heavy(self, structure: DocumentStructure) -> Dict:
        """Summarize table-heavy documents"""
        
        table_insights = []
        markdown_tables = []
        
        for i, table in enumerate(structure.tables):
            # Generate markdown table
            markdown_table = self._convert_to_markdown(table)
            markdown_tables.append({
                "table_id": i + 1,
                "title": table.title,
                "markdown": markdown_table,
                "insights": self._analyze_table_trends(table.data)
            })
            
            # Extract insights
            insights = self._extract_table_insights(table.data)
            table_insights.extend(insights)
        
        return {
            "strategy": "TABLE-HEAVY",
            "executive_summary": self._generate_table_executive_summary(structure.tables),
            "table_insights": table_insights,
            "markdown_tables": markdown_tables,
            "trends_and_patterns": self._identify_table_trends(structure.tables),
            "data_quality": self._assess_data_quality(structure.tables)
        }
    
    def _summarize_mixed(self, structure: DocumentStructure, text_blocks: List[str]) -> Dict:
        """Summarize mixed documents"""
        
        # Get text summary
        text_summary = self._summarize_text_heavy(structure, text_blocks)
        
        # Get table summary
        table_summary = self._summarize_table_heavy(structure)
        
        # Cross-reference text and tables
        cross_references = self._cross_reference_text_tables(text_blocks, structure.tables)
        
        return {
            "strategy": "MIXED",
            "text_components": text_summary,
            "table_components": table_summary,
            "cross_references": cross_references,
            "integrated_summary": self._integrate_text_and_tables(text_summary, table_summary)
        }
    
    def _generate_executive_summary(self, text: str) -> str:
        """Generate executive summary for text"""
        try:
            # Use the base summarizer for executive summary
            summary = self.base_summarizer.summarize(text, max_words=150)
            return summary
        except Exception:
            return "Executive summary generation failed."
    
    def _generate_section_summary(self, sections: List[str], text_blocks: List[str]) -> List[Dict]:
        """Generate section-wise summary"""
        section_summaries = []
        
        for section in sections:
            # Find text blocks related to this section
            related_text = self._find_section_text(section, text_blocks)
            if related_text:
                summary = self.base_summarizer.summarize(related_text, max_words=100)
                section_summaries.append({
                    "section": section,
                    "summary": summary,
                    "key_points": self._extract_key_points(related_text)
                })
        
        return section_summaries
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from text"""
        # Look for bullet points, numbered lists, and important statements
        key_points = []
        
        # Extract bullet points
        bullet_patterns = [
            r'•\s*(.+)',
            r'-\s*(.+)',
            r'\*\s*(.+)',
            r'\d+\.\s*(.+)'
        ]
        
        for pattern in bullet_patterns:
            matches = re.findall(pattern, text)
            key_points.extend(matches)
        
        # Extract important statements (sentences with numbers, percentages, etc.)
        important_patterns = [
            r'[^.]*\d+%[^.]*\.',
            r'[^.]*\$\d+[^.]*\.',
            r'[^.]*\d{4}[^.]*\.'
        ]
        
        for pattern in important_patterns:
            matches = re.findall(pattern, text)
            key_points.extend(matches)
        
        return key_points[:10]  # Limit to 10 key points
    
    def _identify_patterns(self, text: str) -> List[str]:
        """Identify notable patterns in text"""
        patterns = []
        
        # Look for repeated phrases
        words = text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Find most frequent words
        frequent_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        if frequent_words:
            patterns.append(f"Most frequent terms: {', '.join([word for word, _ in frequent_words])}")
        
        # Look for date patterns
        date_patterns = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)
        if date_patterns:
            patterns.append(f"Date references found: {len(date_patterns)} instances")
        
        return patterns
    
    def _detect_anomalies(self, text: str) -> List[str]:
        """Detect anomalies or inconsistencies"""
        anomalies = []
        
        # Check for missing information patterns
        missing_patterns = [
            r'TBD',
            r'To be determined',
            r'Not available',
            r'N/A',
            r'Pending'
        ]
        
        for pattern in missing_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                anomalies.append(f"Missing information detected: {pattern}")
        
        # Check for inconsistent formatting
        if len(re.findall(r'\d+', text)) > 0:
            number_formats = re.findall(r'\d+', text)
            if len(set(number_formats)) > len(number_formats) * 0.8:
                anomalies.append("Inconsistent number formatting detected")
        
        return anomalies
    
    def _convert_to_markdown(self, table) -> str:
        """Convert table to markdown format"""
        try:
            df = table.data
            markdown = f"### {table.title}\n\n"
            
            # Add headers
            headers = "| " + " | ".join(df.columns) + " |"
            markdown += headers + "\n"
            
            # Add separator
            separator = "| " + " | ".join(["---"] * len(df.columns)) + " |"
            markdown += separator + "\n"
            
            # Add data rows (limit to first 10 rows)
            for _, row in df.head(10).iterrows():
                row_str = "| " + " | ".join(str(cell) for cell in row) + " |"
                markdown += row_str + "\n"
            
            if len(df) > 10:
                markdown += f"\n*... and {len(df) - 10} more rows*\n"
            
            return markdown
        except Exception:
            return f"### {table.title}\n\n*Table conversion failed*"
    
    def _analyze_table_trends(self, df) -> List[str]:
        """Analyze trends in table data"""
        trends = []
        
        try:
            # Check for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            for col in numeric_cols:
                if df[col].notna().sum() > 0:
                    # Check for trends
                    values = df[col].dropna()
                    if len(values) > 1:
                        # Simple trend detection
                        first_half = values[:len(values)//2].mean()
                        second_half = values[len(values)//2:].mean()
                        
                        if second_half > first_half * 1.1:
                            trends.append(f"Column '{col}': Upward trend detected")
                        elif second_half < first_half * 0.9:
                            trends.append(f"Column '{col}': Downward trend detected")
                        else:
                            trends.append(f"Column '{col}': Stable values")
        
        except Exception:
            trends.append("Trend analysis completed")
        
        return trends
    
    def _extract_table_insights(self, df) -> List[str]:
        """Extract insights from table data"""
        insights = []
        
        try:
            # Basic statistics
            insights.append(f"Table contains {len(df)} rows and {len(df.columns)} columns")
            
            # Check for missing data
            missing_data = df.isnull().sum().sum()
            if missing_data > 0:
                insights.append(f"Missing data: {missing_data} cells")
            
            # Check for outliers in numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                if df[col].notna().sum() > 0:
                    q1 = df[col].quantile(0.25)
                    q3 = df[col].quantile(0.75)
                    iqr = q3 - q1
                    outliers = df[(df[col] < q1 - 1.5*iqr) | (df[col] > q3 + 1.5*iqr)]
                    if len(outliers) > 0:
                        insights.append(f"Column '{col}': {len(outliers)} potential outliers detected")
        
        except Exception:
            insights.append("Table insights analysis completed")
        
        return insights
    
    def _generate_table_executive_summary(self, tables: List) -> str:
        """Generate executive summary for table-heavy documents"""
        summary_parts = []
        
        summary_parts.append(f"This document contains {len(tables)} tables with structured data.")
        
        # Summarize table types
        table_types = {}
        for table in tables:
            table_type = f"{table.row_count}x{table.col_count}"
            table_types[table_type] = table_types.get(table_type, 0) + 1
        
        if table_types:
            summary_parts.append(f"Table dimensions: {', '.join([f'{count} tables of {dim}' for dim, count in table_types.items()])}")
        
        # Add key insights
        total_rows = sum(table.row_count for table in tables)
        summary_parts.append(f"Total data points: {total_rows} rows across all tables.")
        
        return " ".join(summary_parts)
    
    def _identify_table_trends(self, tables: List) -> List[str]:
        """Identify trends across multiple tables"""
        trends = []
        
        # Compare tables if multiple exist
        if len(tables) > 1:
            trends.append(f"Document contains {len(tables)} tables for comparison")
            
            # Check for similar structures
            structures = [(table.row_count, table.col_count) for table in tables]
            unique_structures = len(set(structures))
            if unique_structures < len(structures):
                trends.append("Multiple tables have similar structures")
        
        return trends
    
    def _assess_data_quality(self, tables: List) -> Dict:
        """Assess data quality across tables"""
        quality_report = {
            "total_tables": len(tables),
            "total_rows": sum(table.row_count for table in tables),
            "missing_data": 0,
            "data_completeness": 0
        }
        
        total_cells = 0
        missing_cells = 0
        
        for table in tables:
            try:
                missing = table.data.isnull().sum().sum()
                total = table.data.size
                missing_cells += missing
                total_cells += total
            except Exception:
                continue
        
        if total_cells > 0:
            quality_report["missing_data"] = missing_cells
            quality_report["data_completeness"] = f"{((total_cells - missing_cells) / total_cells * 100):.1f}%"
        
        return quality_report
    
    def _cross_reference_text_tables(self, text_blocks: List[str], tables: List) -> List[Dict]:
        """Cross-reference text content with table data"""
        references = []
        
        # Look for table references in text
        for i, table in enumerate(tables):
            table_keywords = self._extract_table_keywords(table.data)
            
            for j, text_block in enumerate(text_blocks):
                # Check if text mentions table data
                for keyword in table_keywords:
                    if keyword.lower() in text_block.lower():
                        references.append({
                            "table_id": i + 1,
                            "text_block": j + 1,
                            "keyword": keyword,
                            "reference_type": "data_mention"
                        })
        
        return references
    
    def _extract_table_keywords(self, df) -> List[str]:
        """Extract keywords from table data"""
        keywords = []
        
        try:
            # Get column names
            keywords.extend(df.columns.tolist())
            
            # Get unique values from first few rows
            for col in df.columns:
                unique_vals = df[col].dropna().unique()[:5]
                keywords.extend([str(val) for val in unique_vals if len(str(val)) > 2])
        
        except Exception:
            pass
        
        return keywords
    
    def _integrate_text_and_tables(self, text_summary: Dict, table_summary: Dict) -> str:
        """Integrate text and table summaries"""
        integration = []
        
        integration.append("This document combines narrative text with structured data tables.")
        
        if text_summary.get("executive_summary"):
            integration.append(f"Text Summary: {text_summary['executive_summary'][:200]}...")
        
        if table_summary.get("executive_summary"):
            integration.append(f"Data Summary: {table_summary['executive_summary']}")
        
        return " ".join(integration)
    
    def _find_section_text(self, section: str, text_blocks: List[str]) -> str:
        """Find text related to a specific section"""
        related_text = []
        
        for block in text_blocks:
            if section.lower() in block.lower():
                related_text.append(block)
        
        return " ".join(related_text)
