import httpx

from fastapi import HTTPException

from src.core.constant_manger import ESP32_URL


class GateClient:
    async def open_gate(self):
        try:
            async with httpx.AsyncClient() as client:

                response = await client.post(
                    f"{ESP32_URL}/open"
                )

                if response.status_code != 200:

                    raise HTTPException(
                        status_code=500,
                        detail="Failed to open gate"
                    )

                return response.json()

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    async def lock_gate(self):

        try:

            async with httpx.AsyncClient() as client:

                response = await client.post(
                    f"{ESP32_URL}/lock"
                )

                if response.status_code != 200:

                    raise HTTPException(
                        status_code=500,
                        detail="Failed to lock gate"
                    )

                return response.json()

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )