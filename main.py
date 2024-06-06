from typing import Any
import flet as ft


class Song(object):
    def __init__(self, song_name: str, artist_name: str,
        audio_path: str, img_path: str) -> None:
        super(Song, self).__init__()
        self.song_name: str = song_name
        self.artist_name: str = artist_name
        self.audio_path: str = audio_path
        self.img_path: str = img_path 

    @property
    def name(self) -> str:
        return self.song_name
    
    @property
    def artist(self) -> str:
        return self.artist_name
    
    @property
    def path(self):
        return self.audio_path
    
    @property
    def path_img(self):
        return self.img_path


class AudiDirectory(object):

    playlist: list = [
        Song(
            song_name="Genres Hiphop",
            artist_name="Desconhecido",
            audio_path="Genres Hiphop.mp3",
            img_path="img.jpg"
        ),
        Song(
            song_name="Genres EDM",
            artist_name="Desconhecido",
            audio_path="Genres EDM.mp3",
            img_path="img.jpg"
        )
    ]


class Playlist(ft.View):
    def __init__(self, page: ft.Page):
        super(Playlist, self).__init__(
            route="/playlist",
            horizontal_alignment="center"
        )
        
        self.page = page
        self.playlist: list[Song] = AudiDirectory.playlist

        self.controls = [
            ft.Row(
                [
                    ft.Text("PLAYLIST", size=21, weight="bold"),
                ],
                alignment="center"
            ),
            ft.Divider(height=10, color="transparent")
        ]

        self.gerenate_playlist_ui()

    def gerenate_playlist_ui(self) -> None:
        for song in self.playlist:
            self.controls.append(
                self.create_song_row(
                    song_name=song.song_name,
                    artist_name=song.artist_name,
                    song=song
                )
            )
    
    def create_song_row(self, song_name, artist_name, song: Song) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(f"Title: {song.name}"),
                    ft.Text(artist_name)
                ],
                alignment="spaceBetween"
            ),
            data=song,
            padding=10,
            on_click=self.toogle_song
        )

    def toogle_song(self, e):
        self.page.session.set("song", e.control.data)
        self.page.go("/song")


class CurrentSong(ft.View):
    def __init__(self, page: ft.Page) -> None:
        super(CurrentSong, self).__init__(
            route="/song",
            padding=20,
            horizontal_alignment="center",
            vertical_alignment="center",
        )

        self.page = page
        self.song = self.page.session.get("song")
        self.create_audio_track()

        
        self.duration: int = 0
        self.start: int = 0
        self.end: int = 0

        self.is_playing: bool = False

        
        self.txt_start = ft.Text(self.format_time(self.start))
        self.txt_end = ft.Text(f"-{self.format_time(
            self.start)}")
                
        self.slider = ft.Slider(
            min=0,
            thumb_color="transparent", 
            on_change_end=lambda e: self.toggle_seek(
                round(float(e.data))
            )
            )
        
        self.back_btn = ft.TextButton(
            content=ft.Text(
                "Playlist",
                color="black"
                if self.page.theme_mode == ft.ThemeMode.LIGHT
                else "white"
            ),
            on_click=self.toggle_playlist,
        )

        self.play_btn: Any = self.create_toogle_button(
            ft.icons.PLAY_ARROW_ROUNDED, 2, self.play
        )

        
        self.controls = [
            ft.Row([self.back_btn], alignment="start"),
            ft.Container(
                height=120,
                expand=True,
                border_radius=8,
                shadow=ft.BoxShadow(
                    spread_radius=6,
                    blur_radius=10,
                    color=ft.colors.with_opacity(0.35,
                        "black"),
                ),
                image_fit="cover",
                image_src=self.song.path_img,
            ),
            ft.Divider(height=10, color="transparent"),
            ft.Column(
                [
                    ft.Row(
                        controls=[ft.Text(self.song.name,
                            size=18, weight="bold")],
                    ),
                    ft.Row(
                        controls=[ft.Text(self.song.name,
                            size=18, opacity=0.81)],
                    ),
                ],
                spacing=1,
            ),
            ft.Divider(height=10, color="transparent"),
            ft.Column(
                [
                    ft.Row([self.txt_start, self.txt_end],
                        alignment="spaceBetween"),                 
                    self.slider
                    
                ],
                spacing=0,
            ),
            ft.Divider(height=10, color="transparent"),
            ft.Row(
                [
                    self.create_toogle_button(
                        ft.icons.REPLAY_10_SHARP,
                        0.9,
                        lambda e: self.__update_position(-500)
                    ),
                    self.play_btn,
                    self.create_toogle_button(
                        ft.icons.FORWARD_10_SHARP,
                        0.9,
                        lambda e: self.__update_position(500)
                    )
                ],
                alignment="spaceEvenly",
            ),
            ft.Divider(height=10, color="transparent"),
        ]

    def play(self, e) -> None:
        self.toggle_play_pause()
        self.duration = self.audio.get_duration()
        self.end = self.duration
        self.slider.max = self.duration

    def toggle_play_pause(self, event=None):
        if self.is_playing:
            self.play_btn.icon = ft.icons.PLAY_ARROW_ROUNDED
            self.audio.pause()
        else:
            self.play_btn.icon = ft.icons.PAUSE_ROUNDED
            try:
                self.audio.resume()
            except Exception:
                self.audio.play()
        
        self.is_playing = False if self.is_playing else True
        self.play_btn.update()

    def __update_start_end(self) -> None:
        if self.start < 0:
            self.start = 0
        
        if self.end > self.duration:
            self.end = self.duration

    def __update_position(self, delta: int) -> None:
       
        self.__update_start_end()

        pos_change = 0
        if self.start > 0:
            if delta == 5000:
                pos_change = 5000
            elif delta == -5000:
                pos_change = -5000

        pos: int = (
            self.start + pos_change
        ) 
        self.audio.seek(pos)

        self.start += pos_change
        self.end -= pos_change

    def __update_slider(self, delta: int) -> None:
        self.slider.value = delta
        self.slider.update()

    def __update_time_stamps(self, start: int, end: int) -> None:
        self.txt_start.value = self.format_time(start)
        self.txt_end.value = f"-{self.format_time(end)}"

        self.txt_start.update()
        self.txt_end.update()

    def toggle_seek(self, delta):
        self.start = delta
        self.end = self.duration - delta

        self.audio.seek(self.start)
        self.__update_slider(delta)

    def __update(self, delta: int):
        self.start += 1000
        self.end -= 1000
        
        self.__update_slider(delta) 
        self.__update_time_stamps(self.start, self.end)

    def format_time(self, value: int) -> str:
        milliseconds: int = value
        
        minutes, seconds = divmod(milliseconds / 1000, 60)
        
        formatted_time: str = "{:02}:{:02}".format(int(minutes), int(seconds))
        
        return formatted_time

    def create_audio_track(self) -> None:
        self.audio = ft.Audio(
            src=self.song.path,
            on_position_changed=lambda e: self.__update(
                int(e.data)
            )
        )

        self.page.overlay.append(self.audio)

    def create_toogle_button(self, icon, scale, function) -> ft.IconButton:
        return ft.IconButton(icon=icon, scale=scale, on_click=function)
    

    def toggle_playlist(self, e) -> None:
        self.audio.pause()
        self.page.session.clear()
        self.page.go("/playlist")
        pass

def main(page: ft.Page) -> None:
    page.theme_mode = ft.ThemeMode.LIGHT
    
    def router(route):
        page.views.clear()

        if page.route == "/playlist":
            playlist = Playlist(page)
            page.views.append(playlist)

        if page.route == "/song":
            song =CurrentSong(page)
            page.views.append(song)

        page.update()
    
    page.on_route_change = router
    page.go('/playlist')

ft.app(target=main, assets_dir="assets")