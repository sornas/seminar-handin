from pathlib import Path

from aiohttp import web

routes = web.RouteTableDef()

TEACHER_SECRET = "teacher123"


@routes.get("/")
async def hello(request):
    return web.Response(text="Hello, world")

@routes.get("/student")
async def student(request):
    with open("html/templates/student.html") as f:
        return web.Response(body=f.read(), content_type="text/html")

@routes.get(f"/{TEACHER_SECRET}")
async def teacher(request):
    with open("html/templates/teacher.html") as f:
        return web.Response(body=f.read(), content_type="text/html")

@routes.get(f"/{TEACHER_SECRET}/handins/{{uid}}")
async def teacher_handin(request):
    uid = request.match_info["uid"]
    path = Path(f"handins/{uid}")
    if not path.exists():
        return web.Response(text=f"Invalid uid {uid}", status=400)
    with path.open() as f:
        return web.Response(text="<code>" + f.read().replace("\n", "<br>").replace(" ", "&nbsp;") + "</code>")

if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)
