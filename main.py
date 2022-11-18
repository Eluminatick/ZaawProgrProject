from datetime import datetime
from io import BytesIO

from PIL import Image, ImageOps
from fastapi import Depends, FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sympy import isprime

description = """ The safety words are banana."""
app = FastAPI(title="Program Zaliczeniowy Daniel Dystrych",
              description=description,
              version="First and last",
              )


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/prime/{n}")
async def is_prime(n: str):
    try:
        n = int(n)
        return {f"Is {n} Prime?": str(isprime(n))}
    except ValueError:
        return {"ValueError": "You didn't provided number"}
    except Exception as e:
        return {'Exception': str(e)}


@app.post("/picture/invert")
async def invert(picture: UploadFile = File(...)):
    img = Image.open(picture.file)
    img = ImageOps.invert(img)

    inverted_img = BytesIO()
    img.save(inverted_img, "JPEG")
    inverted_img.seek(0)

    return StreamingResponse(inverted_img, media_type="image/jpeg")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hashing(password: str):
    return "hashed" + password


user_db = {"banana": {"username": "banana",
                      "hashed_password": "banana"}
           }


def password_hashing(password: str):
    return "hashed" + password


@app.post('/token')
async def tokennize(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username not in user_db:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if password_hashing(form_data.password) != user_db.get(form_data.username).get('hashed_password'):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": form_data.username + "_token", "token_type": "bearer"}


@app.get('/time')
async def time(token: str = Depends(oauth2_scheme)):
    return {"Current server date and time": datetime.now()}

