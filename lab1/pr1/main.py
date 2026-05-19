from fastapi import FastAPI
from pr1.models import Warrior, Profession
from typing import List
from typing_extensions import TypedDict
from pr1.db import temp_bd, professions_bd


app = FastAPI()


@app.get("/warriors_list")
def warriors_list() -> List[Warrior]:
    return temp_bd


@app.get("/warrior/{warrior_id}")
def warriors_get(warrior_id: int) -> List[Warrior]:
    return [warrior for warrior in temp_bd if warrior.get("id") == warrior_id]


@app.post("/warrior")
def warriors_create(warrior: Warrior) -> TypedDict('Response', {"status": int, "data": Warrior}):
    warrior_to_append = warrior.model_dump()
    temp_bd.append(warrior_to_append)
    return {"status": 200, "data": warrior}


@app.delete("/warrior/delete{warrior_id}")
def warrior_delete(warrior_id: int):
    for i, warrior in enumerate(temp_bd):
        if warrior.get("id") == warrior_id:
            temp_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/warrior{warrior_id}")
def warrior_update(warrior_id: int, warrior: Warrior) -> List[Warrior]:
    for war in temp_bd:
        if war.get("id") == warrior_id:
            warrior_to_append = warrior.model_dump()
            temp_bd.remove(war)
            temp_bd.append(warrior_to_append)
    return temp_bd


@app.get("/professions_list")
def professions_list() -> List[Profession]:
    return professions_bd


@app.get("/profession/{profession_id}")
def profession_get(profession_id: int) -> List[Profession]:
    return [p for p in professions_bd if p.get("id") == profession_id]


@app.post("/profession")
def profession_create(profession: Profession) -> TypedDict('Response', {"status": int, "data": Profession}):
    professions_bd.append(profession.model_dump())
    return {"status": 200, "data": profession}


@app.delete("/profession/delete{profession_id}")
def profession_delete(profession_id: int):
    for i, profession in enumerate(professions_bd):
        if profession.get("id") == profession_id:
            professions_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/profession{profession_id}")
def profession_update(profession_id: int, profession: Profession) -> List[Profession]:
    for p in professions_bd:
        if p.get("id") == profession_id:
            professions_bd.remove(p)
            professions_bd.append(profession.model_dump())
    return professions_bd
