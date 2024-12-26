from fastapi import UploadFile

from live_chat.web.enums import UploadFileDirectoryEnum
from live_chat.web.utils import FileSaver


async def check_image(uploaded_image: UploadFile) -> str | None:
    """A function that checks for the presence of a photo."""
    if not uploaded_image.filename:
        return ""

    image_saver = FileSaver()
    return await image_saver.save_file(
        uploaded_image,
        UploadFileDirectoryEnum.avatars,
    )
