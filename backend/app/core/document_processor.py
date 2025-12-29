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
        """Extract text from PDF file with enhanced extraction"""
        text_content = []
        page_map = {}

        try:
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                num_pages = len(pdf_reader.pages)

                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()

                    # Clean up extracted text
                    if page_text:
                        page_text = page_text.strip()
                        # Remove excessive whitespace while preserving structure
                        lines = [line.strip() for line in page_text.split('\n') if line.strip()]
                        page_text = '\n'.join(lines)

                    text_content.append(page_text if page_text else "")
                    page_map[page_num] = page_text if page_text else ""

            full_text = "\n\n".join([text for text in text_content if text])

            # Calculate statistics
            total_chars = len(full_text)
            pages_with_text = sum(1 for text in text_content if text)

            logger.info(f"Extracted text from PDF: {num_pages} pages, {pages_with_text} pages with text, {total_chars} characters")

            # If no text extracted, provide helpful message in metadata
            if total_chars == 0:
                logger.warning(f"PDF has {num_pages} pages but no extractable text. May be scanned images.")

            return {
                "text": full_text,
                "pages": page_map,
                "metadata": {
                    "num_pages": num_pages,
                    "pages_with_text": pages_with_text,
                    "total_characters": total_chars
                }
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
        """Extract text from CSV file with data analysis support"""
        try:
            df = pd.read_csv(file_path)
            original_rows = len(df)
            original_columns = len(df.columns)

            # Limit rows to prevent token overflow (max 50000 rows)
            if len(df) > 50000:
                df = df.head(50000)

            # Build comprehensive data analysis text
            text_parts = []

            # 1. METADATA SECTION
            metadata_summary = f"""=== CSV FILE METADATA ===
Total Rows: {original_rows}
Total Columns: {original_columns}
Column Names: {', '.join(df.columns.astype(str))}

"""
            text_parts.append(metadata_summary)

            # 2. COLUMN DETAILS WITH DATA TYPES AND STATISTICS
            column_details = "=== COLUMN DETAILS ===\n"
            for col in df.columns:
                col_dtype = str(df[col].dtype)
                non_null = df[col].notna().sum()
                null_count = df[col].isna().sum()

                column_details += f"\nColumn: {col}\n"
                column_details += f"  - Data Type: {col_dtype}\n"
                column_details += f"  - Non-Null Values: {non_null}\n"
                column_details += f"  - Null Values: {null_count}\n"

                # Numeric column statistics
                if pd.api.types.is_numeric_dtype(df[col]):
                    try:
                        column_details += f"  - Min: {df[col].min()}\n"
                        column_details += f"  - Max: {df[col].max()}\n"
                        column_details += f"  - Mean: {df[col].mean():.2f}\n"
                        column_details += f"  - Median: {df[col].median():.2f}\n"
                        column_details += f"  - Std Dev: {df[col].std():.2f}\n"
                    except:
                        pass

                # Categorical/Object column statistics
                else:
                    unique_count = df[col].nunique()
                    column_details += f"  - Unique Values: {unique_count}\n"
                    if unique_count <= 20:
                        top_values = df[col].value_counts().head(10)
                        column_details += f"  - Top Values: {', '.join([f'{v}({c})' for v, c in top_values.items()])}\n"

            text_parts.append(column_details)

            # 3. SAMPLE DATA ROWS (First 20 rows in tabular format)
            sample_rows = min(20, len(df))
            sample_data = f"\n=== SAMPLE DATA (First {sample_rows} rows) ===\n"
            sample_data += df.head(sample_rows).to_string(index=True, max_colwidth=100)
            text_parts.append(sample_data)

            # 4. FULL DATA VALUES (Column-by-column for better context)
            full_data_section = f"\n\n=== COMPLETE DATA VALUES ===\n"
            full_data_section += f"(Showing first {len(df)} of {original_rows} rows)\n\n"

            for col in df.columns:
                col_str = df[col].astype(str)
                # Truncate individual cell values to 500 chars
                col_str = col_str.apply(lambda x: x[:500] if len(x) > 500 else x)
                full_data_section += f"Column '{col}':\n"
                full_data_section += col_str.to_string(max_rows=100, index=True)
                full_data_section += "\n\n"

            text_parts.append(full_data_section)

            if original_rows > 50000:
                text_parts.append(f"\n[Note: Showing first 50000 of {original_rows} total rows]")

            # Combine all sections
            text = "\n".join(text_parts)

            # Check total size
            if len(text) > 100000:
                logger.warning(f"CSV file produced {len(text)} chars, truncating to 100000")
                text = text[:100000] + "\n\n[Content truncated due to size]"

            logger.info(f"Extracted CSV with analysis: {len(df)} rows, {len(df.columns)} columns")

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
        """Extract text from Excel file with data analysis support"""
        excel_file = None
        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_map = {}
            all_sheets_text = []

            # Collect sheet metadata
            sheet_metadata = []
            total_rows = 0

            # Create metadata summary at the beginning
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                original_rows = len(df)
                total_rows += original_rows
                sheet_metadata.append(f"  - {sheet_name}: {original_rows} rows, {len(df.columns)} columns")

            metadata_summary = f"""=== EXCEL FILE METADATA ===
Total Sheets: {len(excel_file.sheet_names)}
Total Rows (all sheets): {total_rows}
Sheet Details:
{chr(10).join(sheet_metadata)}

"""
            all_sheets_text.append(metadata_summary)

            # Process each sheet with detailed analysis
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                original_rows = len(df)

                # Limit rows to prevent token overflow (max 50000 rows per sheet)
                if len(df) > 50000:
                    df = df.head(50000)

                sheet_parts = []

                # Sheet header
                sheet_header = f"\n{'='*60}\nSHEET: {sheet_name}\n{'='*60}\n"
                if original_rows > 50000:
                    sheet_header += f"(Showing first 50000 of {original_rows} rows)\n"
                sheet_parts.append(sheet_header)

                # Column details with statistics
                column_details = "\n=== COLUMN DETAILS ===\n"
                for col in df.columns:
                    col_dtype = str(df[col].dtype)
                    non_null = df[col].notna().sum()
                    null_count = df[col].isna().sum()

                    column_details += f"\nColumn: {col}\n"
                    column_details += f"  - Data Type: {col_dtype}\n"
                    column_details += f"  - Non-Null Values: {non_null}\n"
                    column_details += f"  - Null Values: {null_count}\n"

                    # Numeric column statistics
                    if pd.api.types.is_numeric_dtype(df[col]):
                        try:
                            column_details += f"  - Min: {df[col].min()}\n"
                            column_details += f"  - Max: {df[col].max()}\n"
                            column_details += f"  - Mean: {df[col].mean():.2f}\n"
                            column_details += f"  - Median: {df[col].median():.2f}\n"
                            column_details += f"  - Std Dev: {df[col].std():.2f}\n"
                        except:
                            pass

                    # Categorical/Object column statistics
                    else:
                        unique_count = df[col].nunique()
                        column_details += f"  - Unique Values: {unique_count}\n"
                        if unique_count <= 20:
                            top_values = df[col].value_counts().head(10)
                            column_details += f"  - Top Values: {', '.join([f'{v}({c})' for v, c in top_values.items()])}\n"

                sheet_parts.append(column_details)

                # Sample data rows (First 20 rows in tabular format)
                sample_rows = min(20, len(df))
                sample_data = f"\n=== SAMPLE DATA (First {sample_rows} rows) ===\n"
                sample_data += df.head(sample_rows).to_string(index=True, max_colwidth=100)
                sheet_parts.append(sample_data)

                # Full data values (Column-by-column)
                full_data_section = f"\n\n=== COMPLETE DATA VALUES ===\n"
                for col in df.columns:
                    col_str = df[col].astype(str)
                    # Truncate individual cell values to 500 chars
                    col_str = col_str.apply(lambda x: x[:500] if len(x) > 500 else x)
                    full_data_section += f"Column '{col}':\n"
                    full_data_section += col_str.to_string(max_rows=100, index=True)
                    full_data_section += "\n\n"

                sheet_parts.append(full_data_section)

                # Combine all sheet parts
                sheet_text = "\n".join(sheet_parts)
                all_sheets_text.append(sheet_text)
                sheet_map[sheet_name] = sheet_text

            # Combine all sheets
            full_text = "\n\n".join(all_sheets_text)

            # Check if text is too large
            if len(full_text) > 100000:
                logger.warning(f"Excel file produced {len(full_text)} chars, truncating to 100000")
                full_text = full_text[:100000] + "\n\n[Content truncated due to size]"

            logger.info(f"Extracted Excel with analysis: {len(excel_file.sheet_names)} sheets, {total_rows} total rows")

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
 
