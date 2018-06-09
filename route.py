# -*- coding: utf-8 -*-
import json
from flask import Flask, jsonify, abort, make_response
from station import Station
from line import Line

def create_app():
    app = Flask(__name__)

    @app.route('/station/<string:lineId>/<string:pageId>', methods=['GET'])
    def get_station_timetable(lineId, pageId):
        STA = Station("http://www.ekikara.jp/newdata/ekijikoku/" + lineId + "/" + pageId + ".htm")
        timetable = STA.get_timetable()
        # return make_response(jsonify({"timetable": timetable}), 200)
        response = make_response(json.dumps({"timetable": timetable}, ensure_ascii=False, sort_keys=True, separators=(',', ': ')), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

    @app.errorhandler(500)
    def server_error(error):
        return make_response(jsonify({'error': 'Server Error'}), 500)

    return app
