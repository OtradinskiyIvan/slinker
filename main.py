from presentations.api_app import create_app
import uvicorn
from fastapi.testclient import TestClient


if __name__ == '__main__':
    app = create_app()
    uvicorn.run(app)
    '''test_cli = TestClient(app)
    resp = test_cli.post("/link", json={"l_link": "https://google.com"})
    print(resp.json()["s_link"])'''