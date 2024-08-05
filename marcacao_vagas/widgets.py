import tkinter as tk

def create_widgets(app):
    app.frame_left_side = tk.Frame(app.master)
    app.frame_right_side = tk.Frame(app.master)
    app.video_progress_bar = tk.Scale(app.frame_right_side, from_=0, to=100, orient=tk.HORIZONTAL, command=app.update_frame_from_progress)
    app.frame_buttons_player = tk.Frame(app.frame_right_side)
    app.frame_referenced_video_frame = tk.Frame(app.master)
    app.frame_left_side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    app.frame_menu = tk.Frame(app.frame_left_side)
    app.frame_menu["pady"] = 20
    app.frame_menu["padx"] = 20
    app.frame_menu.pack(side=tk.TOP)
    app.btn_selecionar_video = tk.Button(app.frame_menu, text="Selecionar Vídeo", command=app.open_video)
    app.btn_selecionar_video.pack(fill=tk.X)
    app.btn_selecionar_frame_referencia = tk.Button(app.frame_menu, text="Selecionar Frame de Referência", command=app.select_reference_frame, state=tk.DISABLED)
    app.btn_selecionar_frame_referencia.pack(fill=tk.X)
    app.btn_selecionar_demarcacoes = tk.Button(app.frame_menu, text="Selecionar Demarcações", state=tk.DISABLED, command=app.select_markings)
    app.btn_selecionar_demarcacoes.pack(fill=tk.X)
    app.btn_processar = tk.Button(app.frame_menu, text="Processar", state=tk.DISABLED, command=app.processing_video)
    app.btn_processar.pack(fill=tk.X)
