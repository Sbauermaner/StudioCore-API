# StudioCore Pilgrim API

**Что делает**  
Вставляешь лирику → ядро StudioCore анализирует (эмоции, TLP, метр, резонанс, безопасность), 
подбирает жанр/тональность/BPM/вокал/инструменты и строит **Suno style prompt**. 
Можно получить **чистый отформатированный текст со скелетом** для копирования в Suno.

## Запуск локально

```bash
pip install -r requirements.txt
uvicorn app_fastapi:app --reload --port 7860
