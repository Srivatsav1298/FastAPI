from fastapi import FastAPI, Body, Response, status, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
# The below library is to map the retrieved value to its respective column name.
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db

# Creates the models
# Move the creation of models.Base.metadata inside an event function

app = FastAPI()

@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=engine)

class Post(BaseModel):
    title: str
    content: str
    published: bool=True
    rating: Optional[int]=None
try:
    conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='Ronick58', 
        cursor_factory=RealDictCursor)
    # 'cursor is used to execute SQL statements'
    cursor=conn.cursor()
    print('Database connection was successful')
    
except Exception as error:
    print('Connecting to database failed.')
    print('Error:',error)
    time.sleep(2)

my_posts = [{'title':'title of post 1','content':'content of post 1','id':1},
            {'title':'title of post 2','content':'content of post 2','id':2}]

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i
    return None

@app.get('/')
def root():
    return {'message': 'Hello World'}

@app.get('/sqlalchemy')
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return{'data':posts}

@app.get('/posts')
def get_posts(db: Session = Depends(get_db)):
    #cursor.execute(""" SELECT * FROM posts """)
    #posts=cursor.fetchall()
    posts = db.query(models.Post).all()
    return {'data':posts}

@app.post('/posts', status_code=status.HTTP_201_CREATED)
def create_posts(post:Post,db: Session = Depends(get_db)):
    #cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #    (post.title, post.content, post.published))
    #new_post = cursor.fetchone()
    #conn.commit()
    new_post=models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {'data': new_post}

@app.get('/posts/{id}')
def get_post(id:int, response: Response,db: Session = Depends(get_db)):
    #cursor.execute(""" SELECT * FROM posts WHERE id=%s""",(str(id)))
    #post=cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found.')
    return {'post_detail': post}

@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,db: Session = Depends(get_db)):
    #cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """,(str(id)))
    #deleted_post=cursor.fetchone()
    #   conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} does not exist.')
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put('/posts/{id}')
def update_post(id:int, updated_post:Post, db: Session = Depends(get_db)):
    #cursor.execute(""" UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *""", 
    #    (post.title,post.content, post.published, str(id)))
    #updated_post = cursor.fetchone()
    #conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} does not exist.')
    post_query.update(updated_post.dict(),synchronize_session=False)
    db.commit()
    return {'data': post_query.first()}
