from app_server.controllers.blessing import generate_blessings


def test_generate_blessings():
    """测试生成祝福功能"""
    title = "创业成功"
    try:
        blessings = generate_blessings(title,1)
        print("生成的祝福：")
        for blessing in blessings:
            print(blessing)
    except Exception as e:
        print(f"错误：{str(e)}")

if __name__ == "__main__":
    test_generate_blessings()
