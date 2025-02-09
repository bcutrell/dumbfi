package main

import (
        "image/color"
        "log"

        "github.com/hajimehoshi/ebiten/v2"
)

type App struct{}

func (g *App) Update() error {
        return nil
}

func (g *App) Draw(screen *ebiten.Image) {
    screen.Fill(color.RGBA{0x33, 0x33, 0x33, 0xff})
}

func (g *App) Layout(outsideWidth, outsideHeight int) (int, int) {
        return outsideWidth, outsideHeight
}

func main() {
        w, h := ebiten.Monitor().Size()
        ebiten.SetWindowSize(w, h)
        ebiten.SetWindowTitle("dumbfi")
        ebiten.SetWindowPosition(0, 0)
        ebiten.SetWindowResizingMode(ebiten.WindowResizingModeEnabled)

        app := &App{}
        if err := ebiten.RunGame(app); err != nil {
                log.Fatal(err)
        }
}
