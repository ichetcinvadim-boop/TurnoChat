# -*- coding: utf-8 -*-
"""Island 1.2.10 UI builder. Original license checks remain active."""
import brotli
import hashlib
import json
import os
import re
import struct
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
ORIGINAL = ROOT / "island.exe"
ORIGINAL_SHA = "a6304b297e74116360b6bb1a8ac8b420942fa2bf332c92dce01b178a630faa11"
BUNDLES = {
    "settings": (b"/assets/settings-DKyXEiF7.js", b"/index.html", 40913, 10372856, 0x1409c2a26),
    "main": (b"/assets/island-BrWchjAa.js", b"/assets/x-D7kCLGYo.js", 184800, 10372792, 0x140995783)
}
BT = chr(96)

def swap(js, old, new, label):
    old, new = old.replace("~", BT), new.replace("~", BT)
    n = js.count(old)
    if n != 1:
        raise ValueError("Не найден участок " + label + " (совпадений " + str(n) + ")")
    return js.replace(old, new, 1)

def edit_settings(js):
    js = swap(js, '"data-nav":e.id,"data-now":String(n),onClick:()=>a(e.id),',
        '"data-nav":e.id,"data-now":String(n),style:{display:e.id===~pro~?~none~:void 0},onClick:()=>a(e.id),', "Island Pro в меню")
    js = swap(js, 'hidden:y!==~pro~,className:~flex flex-col gap-4~',
        'hidden:y!==~pro~,style:{display:~none~},className:~flex flex-col gap-4~', "страница Island Pro")
    js = swap(js, 'onClick:()=>void r.quit(),className:~flex h-9 w-full items-center',
        'onClick:()=>void r.quit(),style:{display:~none~},className:~flex h-9 w-full items-center', "кнопка выхода")
    return js

def edit_main(js, key):
    # Activate through original Rust backend; no license bypass.
    before = 'u.webAiPopped().then(t=>e.setState({webAiPopped:t}),()=>void 0),u.bootstrap().then'
    after = (
        'u.webAiPopped().then(t=>e.setState({webAiPopped:t}),()=>void 0),'
        'u.licenseStatus().then(t=>t.source===~key~?null:u.licenseActivate('
        + json.dumps(key, ensure_ascii=False)
        + ')).catch(t=>console.error(~Island activation failed~,t)).then(()=>u.bootstrap()).then'
    )
    js = swap(js, before, after, "автоактивация")
    js = swap(js, 't.trialOver&&e.getState().pushPeek({kind:~pro~,feature:~trial~}),',
        '!1&&t.trialOver&&e.getState().pushPeek({kind:~pro~,feature:~trial~}),', "уведомление trial")
    pat = r'case~pro~:return\(0,F\.jsx\)\(aj,\{.*?onClick:\(\)=>void u\.openSettings\(\)\}\);'.replace("~",BT)
    matches = list(re.finditer(pat, js, re.S))
    if len(matches) != 1:
        raise ValueError("Не найдена ровно одна всплывающая карточка Pro")
    m = matches[0]
    original = m.group()
    hidden = original.replace("case"+BT+"pro"+BT+":return", "case"+BT+"pro"+BT+":return!1?", 1)[:-1] + ":null;"
    js = js[:m.start()] + hidden + js[m.end():]
    js = swap(js, 'function ck({feature:e}){return(0,F.jsx)(~div~,{className:~grid h-full place-items-center~,',
        'function ck({feature:e}){return(0,F.jsx)(~div~,{style:{display:~none~},className:~grid h-full place-items-center~,', "карточка покупки")
    return js

def locate(data, name, next_name, old_len):
    pos = data.find(name)
    if pos < 0 or data.find(name, pos+1) >= 0:
        raise ValueError("Не найден уникальный ресурс " + name.decode())
    a = pos + len(name)
    z = data.find(next_name, a)
    if z-a != old_len:
        raise ValueError("Содержимое Island не соответствует версии 1.2.10")
    return a,z,brotli.decompress(data[a:z]).decode("utf-8")

def pack(js, maximum):
    for level in (9,10,11):
        b = brotli.compress(js.encode("utf-8"), quality=level)
        if len(b) <= maximum:
            if brotli.decompress(b).decode("utf-8") != js:
                raise ValueError("Сжатый JavaScript не прошёл проверку")
            return b
    raise ValueError("Обновлённые файлы интерфейса не помещаются в EXE")

def build(source, key, target):
    source, target = Path(source), Path(target)
    if source.resolve() == target.resolve():
        raise ValueError("Не перезаписывай оригинал island.exe")
    if not key or len(key) > 2048 or any(c in key for c in "\x00\n\r"):
        raise ValueError("Ключ должен быть одной строкой (до 2048 символов)")
    data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != ORIGINAL_SHA:
        raise ValueError("Нужен оригинальный island.exe версии 1.2.10, а не установщик")
    out = bytearray(data)
    for tag, (name,next_name,old_len,ptr_off,expected_address) in BUNDLES.items():
        a,z,js = locate(data,name,next_name,old_len)
        ptr,n = struct.unpack_from("<QQ",data,ptr_off)
        if ptr != expected_address or n != old_len:
            raise ValueError("Указатель ресурса повреждён: " + tag)
        js = edit_settings(js) if tag=="settings" else edit_main(js,key)
        compressed = pack(js,old_len)
        out[a:a+len(compressed)] = compressed
        out[a+len(compressed):z] = b"\x00"*(old_len-len(compressed))
        struct.pack_into("<Q",out,ptr_off+8,len(compressed))
    if len(data) != len(out) or out[:2] != b"MZ":
        raise ValueError("Ошибка структуры EXE")
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".building")
    try:
        tmp.write_bytes(out)
        tmp.replace(target)
    finally:
        if tmp.exists(): tmp.unlink()

def main():
    root = tk.Tk()
    root.title("Island Key Builder · 1.2.10")
    root.geometry("680x390")
    root.minsize(600,360)
    panel = ttk.Frame(root,padding=20)
    panel.pack(fill="both",expand=True)
    ttk.Label(panel,text="Island Key Builder",font=("Segoe UI",19,"bold")).pack(anchor="w")
    ttk.Label(panel,text="Введи ключ → создай Island-Custom.exe. Компоненты лицензии скрываются, а проверка ключа сохраняется.",
              wraplength=630).pack(anchor="w",pady=(5,20))
    ttk.Label(panel,text="Оригинальный island.exe:").pack(anchor="w")
    original = tk.StringVar(value=str(ORIGINAL))
    row = ttk.Frame(panel)
    row.pack(fill="x",pady=(5,12))
    ttk.Entry(row,textvariable=original).pack(side="left",fill="x",expand=True)
    def pick():
        selected = filedialog.askopenfilename(filetypes=[("Windows EXE","*.exe")])
        if selected: original.set(selected)
    ttk.Button(row,text="Обзор…",command=pick).pack(side="right",padx=(8,0))
    ttk.Label(panel,text="Ключ Island Pro:").pack(anchor="w")
    key = tk.StringVar()
    key_row = ttk.Frame(panel)
    key_row.pack(fill="x",pady=(5,10))
    field = ttk.Entry(key_row,textvariable=key,show="•")
    field.pack(side="left",fill="x",expand=True)
    shown = tk.BooleanVar(value=False)
    ttk.Checkbutton(key_row,text="Показать",variable=shown,
        command=lambda: field.configure(show="" if shown.get() else "•")).pack(side="right",padx=(10,0))
    state = tk.StringVar(value="Готов к сборке")
    ttk.Label(panel,textvariable=state,wraplength=620).pack(anchor="w",pady=(3,12))
    def start():
        src = Path(original.get().strip())
        secret = key.get().strip()
        if not src.is_file():
            messagebox.showerror("Ошибка","Выбери оригинальный island.exe")
            return
        if not secret:
            messagebox.showerror("Ошибка","Введи ключ")
            return
        dest = filedialog.asksaveasfilename(defaultextension=".exe",
            initialfile="Island-Custom.exe",filetypes=[("Windows EXE","*.exe")])
        if not dest: return
        btn.configure(state="disabled")
        state.set("Собирается Island-Custom.exe…")
        def worker():
            try:
                build(src,secret,dest)
                root.after(0,lambda: state.set("Готово: "+dest))
                root.after(0,lambda: messagebox.showinfo("Готово","Создан:\n"+dest+"\nПроверка ключа выполнится при первом запуске."))
            except Exception as e:
                error = str(e)
                root.after(0,lambda: state.set("Ошибка сборки"))
                root.after(0,lambda: messagebox.showerror("Не удалось собрать",error))
            finally:
                root.after(0,lambda: btn.configure(state="normal"))
        threading.Thread(target=worker,daemon=True).start()
    btn=ttk.Button(panel,text="Создать Island-Custom.exe",command=start)
    btn.pack(fill="x",ipady=8)
    ttk.Label(panel,text="Важно: действительность ключа не гарантируется; не распространяй EXE со своим ключом.",
        wraplength=620).pack(anchor="w",pady=(12,0))
    root.mainloop()

if __name__=="__main__":
    main()
