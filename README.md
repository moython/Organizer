# Desktop Color Organizer

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-1F6AA5?style=for-the-badge" alt="CustomTkinter">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/Status-Experimental-F59E0B?style=for-the-badge" alt="Experimental">
</p>

<p align="center">
  <b>Turn a messy desktop into a clean, colorful workspace with one click.</b>
</p>

<p align="center">
  Desktop Color Organizer is a Python desktop app that previews, organizes, and themes your Desktop into beautifully grouped folders.
</p>

---

## Preview

Desktop Color Organizer helps you sort files into clean categories like Documents, Images, Videos, Code, Archives, and Apps & Shortcuts. Instead of instantly moving everything without warning, the app shows a preview first, which makes it feel safer and much more professional for real users.

The project was built as a fun Python GUI idea that is also perfect for a YouTube coding video, because the before-and-after transformation is easy to show and instantly satisfying.

## Features

- Beautiful desktop cleanup with category-based organization
- Color-themed folders for a more aesthetic setup
- Preview mode before moving files
- Undo support for the last organize action
- Custom color picker for category themes
- Built with Python + CustomTkinter
- Great beginner-to-intermediate automation project

## Themes

The app currently includes several built-in visual styles:

- **Ocean** – cool blue and cyan tones
- **Sunset** – warm orange, pink, and gold tones
- **Forest** – green-based natural palette
- **Pastel** – soft light colors for a clean gentle look
- **Monochrome** – minimal grayscale aesthetic

You can also create your own custom look by choosing different colors for each category.

## Why this project is cool

A lot of file organizer scripts are useful, but they do not feel like real software. This project tries to make file organization look visual, clean, and fun, while still being practical.

It is also a strong GitHub project because it combines Python automation, file handling, GUI design, themes, and user-focused features like preview and undo.

## Demo idea

A great demo flow for this project is:

1. Show a messy desktop or test folder
2. Open the app
3. Pick a theme
4. Preview the layout
5. Click organize
6. Show the clean result
7. Mention the GitHub repo and source code

That format works very well for short-form or long-form coding content.

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/desktop-color-organizer.git
cd desktop-color-organizer
```

Install dependencies:

```bash
pip install customtkinter pillow
```

Run the app:

```bash
python desktop_color_organizer.py
```

## Safe testing

Before using this on your real desktop, create a test folder with fake files and shortcuts. Then point the app to that folder first so you can test preview, organize, theme, and undo safely.

This is the best way to avoid mistakes while you are still improving the project.

## Project structure

```bash
Desktop-Color-Organizer/
├── desktop_color_organizer.py
├── README.md
└── assets/
```

## Roadmap

Planned improvements for future versions:

- Drag-and-drop category rules
- Better animations inside the app
- Screenshot-ready before/after mode for videos
- Save and load multiple theme presets
- Cleaner settings panel
- Optional desktop shortcut creation
- Better packaging as a Windows executable

## YouTube

I build Python projects, creative tools, and coding content on my YouTube channel:

<p align="center">
  <a href="https://youtube.com/moython" target="_blank">
    <img src="https://img.shields.io/badge/Watch%20on%20YouTube-Moython-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="Moython YouTube Channel">
  </a>
</p>

If you found this project interesting, the channel is where I share the build process, ideas, experiments, and future versions.

## Screenshots

Once you record your video or take screenshots, you can place them in an `assets/` folder and show them like this:

```md
![App Preview](assets/preview.png)
![Theme Preview](assets/theme-preview.png)
```

## Contributing

Suggestions, ideas, and improvements are welcome. If you want to improve the UI, add smarter file rules, or create new themes, contributions are appreciated.

## License

You can use the MIT License for this project if you want it to feel open and easy for others to try, modify, and share.

---

<p align="center">
  Made with Python, creativity, and a slightly unhealthy desire to fix messy desktops.
</p>
