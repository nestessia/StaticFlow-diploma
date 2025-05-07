---
title: Welcome to StaticFlow
template: page.html
---
# Добро пожаловать в StaticFlow!

StaticFlow - это современный генератор статических сайтов с богатыми 
возможностями для создания контента.

## Возможности

### 1. Подсветка кода

```python
def hello_world():
	print("Привет, StaticFlow!")
	
	if True:
		print("Tabs are working!")
		for i in range(3):
			print(f"Tab level {i+1}")
```

Here's some JavaScript with tabs:

```javascript
function testFunction() {
	console.log("Testing tabs");
	
	if (true) {
		console.log("Nested level");
		
		for (let i = 0; i < 3; i++) {
			console.log(`Loop iteration ${i}`);
		}
	}
}
```

### 2. Математические формулы

Inline формула: $E = mc^2$

Блочная формула:
$
\\int_0^\\infty e^{-x} dx = 1
$

### 3. Диаграммы

```mermaid
graph TD;
    A[Начало] --> B[Создание контента];
    B --> C[Сборка сайта];
    C --> D[Публикация];
    D --> E[Конец];
```

### 4. Блоки в стиле Notion

:::info Информация
Это информационный блок. Используйте его для важных заметок.
:::

:::warning Предупреждение
Это блок с предупреждением. Обратите особое внимание!
:::

## Начало работы

1. Создание контента:
   - Добавьте Markdown файлы в директорию `content`
   - Используйте front matter для метаданных

2. Настройка шаблонов:
   - Измените шаблоны в директории `templates`
   - Добавьте свои стили в `static/css`

3. Запуск сервера разработки:
```bash
staticflow serve
``` 