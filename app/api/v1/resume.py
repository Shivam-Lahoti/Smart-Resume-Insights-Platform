from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.parser import extract_text_pdf, extract_text_docx, extract_fields
import logging

logger= logging.getLogger(__name__)


router = APIRouter()

@router.post("/upload")
async def upload_resume(files: list[UploadFile] = File(...)):
    if not (1 <= len(files) <= 2):
        raise HTTPException(status_code=400, detail="You can upload upto 2 files at a time.")
    
    results = []

    for current_file in files: # Iterate through each UploadFile object
        file_result = {"filename": current_file.filename} # Start building result for this file

        if not current_file.filename.endswith((".pdf", ".docx")):

            file_result["error"] = "Invalid file type. Only PDF or DOCX files are allowed."
            file_result["status"] = "failed_validation"
            results.append(file_result)
            continue # Skip to the next file

        try:
            contents = await current_file.read()
            file_result["content_type"] = current_file.content_type
            file_result["size_kb"] = len(contents) / 1024

            text = None
            if current_file.filename.endswith(".pdf"):
                text=  extract_text_pdf(contents)
            elif current_file.filename.endswith(".docx"):
                text= extract_text_docx(contents)
                   
            if text is not None: # Check if text extraction was successful (parser returns None on error)
                file_result["status"] = "processed"
                file_result["message"] = "File processed successfully."
                file_result["preview"] = (text[:997] + "...") if len(text) > 1000 else text
                file_result["extracted_fields"]= extract_fields(text)
                # Store the full 'text' somewhere or pass it for further processing
            else:
                file_result["status"] = "failed_extraction"
                file_result["error"] = "Error extracting text from the file."
                logger.warning(f"Failed to extract text from {current_file.filename}")

        except Exception as e:
            logger.error(f"Error processing file {current_file.filename}: {e}", exc_info=True)
            file_result["status"] = "failed_processing"
            file_result["error"] = f"An unexpected error occurred during processing: {str(e)}"
        
        finally:
            # Ensure the file is closed, especially if spooled to disk
            await current_file.close()
            results.append(file_result)
            
    return results

    

