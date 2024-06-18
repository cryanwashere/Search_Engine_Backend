package main

import (
	"log"
	"os"

	"net/http"
	"github.com/labstack/echo/v4"
)

func main () {
	e := echo.New()
	e.GET("/", func (c echo.Context) error {
		content, err := os.ReadFile("search_page.html")
		if err != nil {
			log.Fatal(err)
		}
		return c.HTML(http.StatusOK, string(content))
	})

	e.Logger.Fatal(e.Start(":1323"))
}