__author__ = 'tomislav'

from flask import render_template,request,session,redirect,url_for,send_from_directory
from app.api_resource import ItemResource,ItemResourceList,SettingsResource, AddAsinsResource, AddUrlsResource

from app.models import Settings


from app import api,app
load_settings = Settings.query.all()

if load_settings:
	USERNAME = load_settings[-1].Username
	PASSWORD = load_settings[-1].Password
else:
	USERNAME = 'test'
	PASSWORD = 'test'

#API
api.add_resource(ItemResource,"/api/<item_id>")
api.add_resource(ItemResourceList,"/api")
api.add_resource(SettingsResource,"/api/settings")
api.add_resource(AddAsinsResource,"/api/addasin")
api.add_resource(AddUrlsResource,"/api/addurls")

#SITE
@app.route("/logout",methods=['GET'])
def logout():
    if session.get('logged_in'):
        session['logged_in'] = False
    return redirect(url_for('index'))

@app.route("/",methods=["GET","POST"])
def index():
    if request.method == 'POST':
        if request.form['p'] == PASSWORD and request.form['u']==USERNAME:
            session['logged_in'] = True

    if session.get('logged_in'):
        return render_template("app/index.html",status=200)
    else:
        return render_template("login/index.html",status=200)

if __name__ == '__main__':
    app.config["SECRET_KEY"] = "ITSASECRET"
    app.run(port=5000,host="0.0.0.0",debug=True)
