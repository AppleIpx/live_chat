from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
from live_chat.db.utils import get_async_session
from live_chat.web.api.chat.utils import validate_user_access_to_chat
from live_chat.web.api.messages.utils import publish_faststream
from live_chat.web.enums import UploadFileDirectoryEnum
from live_chat.web.utils import FileSaver

upload_router = APIRouter()


@upload_router.patch("/{chat_id}/upload-image", summary="Update group image")
async def upload_group_image(
    uploaded_image: UploadFile,
    chat: Chat = Depends(validate_user_access_to_chat),
    db_session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Update group image."""

    image_saver = FileSaver(chat.id)
    image_url = await image_saver.save_file(
        uploaded_image,
        UploadFileDirectoryEnum.group_images,
    )

    if not image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image upload",
        )

    if chat.chat_type.value == "direct":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't specify a photo for direct chat",
        )

    chat.image = image_url
    db_session.add(chat)
    await db_session.commit()
    event_data = jsonable_encoder({"image_url": image_url})
    await publish_faststream("update_image_group", chat.users, event_data, chat.id)
    return {"image_url": image_url}


@upload_router.post("/{chat_id}/upload-attachments")
async def upload_message_file(
    uploaded_file: UploadFile,
    chat: Chat = Depends(validate_user_access_to_chat),
) -> dict[str, str]:
    """Upload a file to use as an attachment in a message."""
    file_saver = FileSaver()
    file_url = await file_saver.save_file(
        uploaded_file,
        f"{UploadFileDirectoryEnum.chat_attachments}/{chat.id}",
    )
    if not file_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file upload",
        )
    return {
        "file_name": file_url.split("/")[-1],
        "file_path": file_url,
    }
