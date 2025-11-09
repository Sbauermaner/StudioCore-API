from studiocore import StudioCore

def main():
    core = StudioCore()
    text = input("Введите текст для анализа: ")
    result = core.analyze(text)
    print(result["prompt"])

if __name__ == "__main__":
    main()
