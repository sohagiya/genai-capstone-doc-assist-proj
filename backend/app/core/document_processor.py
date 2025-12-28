"""Document text extraction from various file formats"""
import hashlib
from pathlib import Path
from typing import Dict, Optional
import PyPDF2
import pandas as pd
from docx import Document
from backend.app.utils.logger import logger


class DocumentProcessor:
    """Extract text from various document formats"""

    @staticmethod
    def compute_hash(file_path: str) -> str:
        """Compute SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def extract_from_pdf(file_path: str) -> Dict[str, any]:
        """Extract text from PDF file"""
        text_content = []
        page_map = {}

        try:
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                num_pages = len(pdf_reader.pages)

                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    text_content.append(page_text)
                    page_map[page_num] = page_text

            full_text = "\n\n".join(text_content)
            logger.info(f"Extracted text from PDF: {num_pages} pages")

            return {
                "text": full_text,
                "pages": page_map,
                "metadata": {"num_pages": num_pages}
            }

        except Exception as e:
            logger.error(f"Error extracting PDF: {str(e)}")
            raise

    @staticmethod
    def extract_from_txt(file_path: str) -> Dict[str, any]:
        """Extract text from TXT file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            logger.info(f"Extracted text from TXT file")

            return {
                "text": text,
                "pages": {0: text},
                "metadata": {"num_pages": 1}
            }

        except Exception as e:
            logger.error(f"Error extracting TXT: {str(e)}")
            raise

    @staticmethod
    def extract_from_csv(file_path: str) -> Dict[str, any]:
        """Extract text from CSV file"""
        try:
            df = pd.read_csv(file_path)
            original_rows = len(df)
            original_columns = len(df.columns)

            # Limit rows to prevent token overflow (max 1000 rows)
            if len(df) > 1000:
                df = df.head(1000)

            # Create metadata summary at the beginning
            metadata_summary = f"""=== CSV FILE METADATA ===
Total Rows: {original_rows}
Total Columns: {original_columns}
Column Names: {', '.join(df.columns.astype(str))}
Data Preview (first {len(df)} rows shown):

"""

            # Convert dataframe to text representation, truncating long values
            text_parts = []
            for col in df.columns:
                col_str = df[col].astype(str)
                # Truncate individual cell values to 500 chars
                col_str = col_str.apply(lambda x: x[:500] if len(x) > 500 else x)
                text_parts.append(f"Column: {col}\n{col_str.to_string(max_rows=100)}")

            data_text = "\n\n".join(text_parts)

            if original_rows > 1000:
                data_text += f"\n\n[Showing first 1000 of {original_rows} rows]"

            # Combine metadata summary with data
            text = metadata_summary + data_text

            # Check total size
            if len(text) > 100000:
                logger.warning(f"CSV file produced {len(text)} chars, truncating to 100000")
                text = text[:100000] + "\n\n[Content truncated due to size]"

            logger.info(f"Extracted text from CSV: {len(df)} rows, {len(df.columns)} columns")

            return {
                "text": text,
                "pages": {0: text},
                "metadata": {"num_rows": original_rows, "num_columns": original_columns}
            }

        except Exception as e:
            logger.error(f"Error extracting CSV: {str(e)}")
            raise

    @staticmethod
    def extract_from_excel(file_path: str) -> Dict[str, any]:
        """Extract text from Excel file"""
        excel_file = None
        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_map = {}
            text_parts = []

            # Collect sheet metadata
            sheet_metadata = []
            total_rows = 0

            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                original_rows = len(df)
                total_rows += original_rows
                sheet_metadata.append(f"  - {sheet_name}: {original_rows} rows, {len(df.columns)} columns")

                # Limit rows to prevent token overflow (max 1000 rows per sheet)
                if len(df) > 1000:
                    df = df.head(1000)
                    sheet_text = f"Sheet: {sheet_name} (showing first 1000 of {original_rows} rows)\n"
                else:
                    sheet_text = f"Sheet: {sheet_name}\n"

                sheet_text += f"Columns: {', '.join(df.columns.astype(str))}\n\n"

                # Convert columns to text, but truncate very long values
                col_texts = []
                for col in df.columns:
                    col_str = df[col].astype(str)
                    # Truncate individual cell values to 500 chars
                    col_str = col_str.apply(lambda x: x[:500] if len(x) > 500 else x)
                    col_texts.append(f"Column: {col}\n{col_str.to_string(max_rows=100)}")

                sheet_text += "\n".join(col_texts)
                text_parts.append(sheet_text)
                sheet_map[sheet_name] = sheet_text

            # Create metadata summary at the beginning
            metadata_summary = f"""=== EXCEL FILE METADATA ===
Total Sheets: {len(excel_file.sheet_names)}
Total Rows (all sheets): {total_rows}
Sheet Details:
{chr(10).join(sheet_metadata)}

Data Preview:

"""

            data_text = "\n\n".join(text_parts)
            full_text = metadata_summary + data_text

            # Check if text is too large (rough estimate: >100K chars might be too much)
            if len(full_text) > 100000:
                logger.warning(f"Excel file produced {len(full_text)} chars, truncating to 100000")
                full_text = full_text[:100000] + "\n\n[Content truncated due to size]"

            logger.info(f"Extracted text from Excel: {len(excel_file.sheet_names)} sheets")

            return {
                "text": full_text,
                "pages": sheet_map,
                "metadata": {"num_sheets": len(excel_file.sheet_names), "total_rows": total_rows}
            }

        except Exception as e:
            logger.error(f"Error extracting Excel: {str(e)}")
            raise
        finally:
            # Ensure file handle is closed
            if excel_file is not None:
                excel_file.close()

    @staticmethod
    def extract_from_docx(file_path: str) -> Dict[str, any]:
        """Extract text from Word DOCX file"""
        try:
            doc = Document(file_path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            text = "\n\n".join(paragraphs)

            logger.info(f"Extracted text from DOCX: {len(paragraphs)} paragraphs")

            return {
                "text": text,
                "pages": {0: text},
                "metadata": {"num_paragraphs": len(paragraphs)}
            }

        except Exception as e:
            logger.error(f"Error extracting DOCX: {str(e)}")
            raise

    def process_document(self, file_path: str, filename: str) -> Dict[str, any]:
        """
        Process a document and extract text based on file type
        Returns dict with text, pages/sheets map, and metadata
        """
        file_ext = Path(filename).suffix.lower()

        # Compute file hash
        file_hash = self.compute_hash(file_path)

        # Extract based on file type
        if file_ext == ".pdf":
            result = self.extract_from_pdf(file_path)
        elif file_ext == ".txt":
            result = self.extract_from_txt(file_path)
        elif file_ext == ".csv":
            result = self.extract_from_csv(file_path)
        elif file_ext in [".xlsx", ".xls"]:
            result = self.extract_from_excel(file_path)
        elif file_ext == ".docx":
            result = self.extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

        # Add file hash to metadata
        result["metadata"]["file_hash"] = file_hash
        result["metadata"]["filename"] = filename
        result["metadata"]["file_type"] = file_ext

        return result
