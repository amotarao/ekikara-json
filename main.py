# -*- coding: utf-8 -*-
import route

app = route.create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000, debug=True)
