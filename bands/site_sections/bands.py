from bands import *


@all_renderable()
class Root:
    def index(self, session, id, message=''):
        return {
            'message': message,
            'band': session.band(id)
        }

    def agreement(self, session, id, message='', **params):
        band = session.band(id)
        band_info = session.band_info(params, restricted=True)
        if cherrypy.request.method == 'POST':
            if not band_info.performer_count:
                message = 'You must tell us how many people are in your band'
            elif not band_info.poc_phone:
                message = 'You must enter an on-site point-of-contact cellphone number'
            elif not band_info.arrival_time:
                message = 'You must enter your expected arrival time'
            elif band_info.bringing_vehicle and not band_info.vehicle_info:
                message = 'You must provide your vehicle information'
            else:
                band.info = band_info
                session.add(band)
                session.add(band_info)
                raise HTTPRedirect('index?id={}&message={}', band.id, 'Your band information has been uploaded')

        return {
            'band': band,
            'band_info': band_info,  # This is currently necessary to prevent custom tags from breaking
            'message': message
        }

    def bio(self, session, id, message='', bio_pic=None, **params):
        band = session.band(id)
        band_bio = session.band_bio(params, restricted=True)
        if cherrypy.request.method == 'POST':
            if not band_bio.desc:
                message = 'Please provide a brief bio for our website'

            if not message and bio_pic.filename:
                band_bio.pic_filename = bio_pic.filename
                band_bio.pic_content_type = bio_pic.content_type.value
                if band_bio.pic_extension not in c.ALLOWED_BIO_PIC_EXTENSIONS:
                    message = 'Bio pic must be one of ' + ', '.join(c.ALLOWED_BIO_PIC_EXTENSIONS)
                else:
                    with open(band_bio.pic_fpath, 'wb') as f:
                        shutil.copyfileobj(bio_pic.file, f)

            if not message:
                band.bio = band_bio
                session.add(band)
                session.add(band_bio)
                raise HTTPRedirect('index?id={}&message={}', band.id, 'Your bio information has been updated')

        return {
            'band': band,
            'message': message
        }

    def w9(self, session, id, message='', w9=None, **params):
        band = session.band(id)
        band_taxes = session.band_taxes(params, restricted=True)
        if cherrypy.request.method == 'POST':
            band_taxes.w9_filename = w9.filename
            band_taxes.w9_content_type = w9.content_type.value
            if band_taxes.w9_extension not in c.ALLOWED_W9_EXTENSIONS:
                message = 'Uploaded file type must be one of ' + ', '.join(c.ALLOWED_W9_EXTENSIONS)
            else:
                with open(band_taxes.w9_fpath, 'wb') as f:
                    shutil.copyfileobj(w9.file, f)
                band.taxes = band_taxes
                session.add(band)
                session.add(band_taxes)
                raise HTTPRedirect('index?id={}&message={}', band.id, 'W9 uploaded')

        return {
            'band': band,
            'message': message
        }

    def stage_plot(self, session, id, message='', plot=None, **params):
        band = session.band(id)
        band_stage_plot = session.band_stage_plot(params, restricted=True)
        if cherrypy.request.method == 'POST':
            band_stage_plot.filename = plot.filename
            band_stage_plot.content_type = plot.content_type.value
            if band_stage_plot.stage_plot_extension not in c.ALLOWED_STAGE_PLOT_EXTENSIONS:
                message = 'Uploaded file type must be one of ' + ', '.join(c.ALLOWED_STAGE_PLOT_EXTENSIONS)
            else:
                with open(band_stage_plot.fpath, 'wb') as f:
                    shutil.copyfileobj(plot.file, f)
                band.stage_plot = band_stage_plot
                session.add(band)
                session.add(band_stage_plot)
                raise HTTPRedirect('index?id={}&message={}', band.id, 'Stage directions uploaded')

        return {
            'band': band,
            'message': message
        }

    def panel(self, session, id, message='', **params):
        band = session.band(id)
        band_panel = session.band_panel(params, checkgroups=['tech_needs'])
        if cherrypy.request.method == 'POST':
            if not band_panel.wants_panel:
                band_panel.wants_panel = 0
                band_panel.name = band_panel.length = band_panel.desc = band_panel.tech_needs = ''
            elif not band_panel.name:
                message = 'Panel Name is a required field'
            elif not band_panel.length:
                message = 'Panel Length is a required field'
            elif not band_panel.desc:
                message = 'Panel Description is a required field'

            if not message:
                band.panel = band_panel
                session.add(band)
                session.add(band_panel)
                raise HTTPRedirect('index?id={}&message={}', band.id, 'Panel preferences updated')

        return {
            'band': band,
            'band_panel': band_panel,  # This is currently necessary to prevent custom tags from breaking
            'message': message
        }

    def rock_island(self, session, id, message='', coverage=False, warning=False, **params):
        band = session.band(id)
        band_merch = session.band_merch(params)
        if cherrypy.request.method == 'POST':
            if not band_merch.selling_merch:
                message = 'You need to tell us whether and how you want to sell merchandise'
            elif band_merch.selling_merch == c.OWN_TABLE and not all([coverage, warning]):
                message = 'You cannot staff your own table without checking the boxes to agree to our conditions'
            else:
                band.merch = band_merch
                session.add(band)
                session.add(band_merch)
                raise HTTPRedirect('index?id={}&message={}', band.id, 'Your merchandise preferences have been saved')

        return {
            'band': band,
            'message': message
        }

    def charity(self, session, id, message='', **params):
        band = session.band(id)
        band_charity = session.band_charity(params)
        if cherrypy.request.method == 'POST':
            if not band_charity.donating:
                message = 'You need to tell is whether you are donating anything'
            elif band_charity.donating == c.DONATING and not band_charity.desc:
                message = 'You need to tell us what you intend to donate'
            else:
                if band_charity.donating == c.NOT_DONATING:
                    band_charity.desc = ''
                band.charity = band_charity
                session.add(band)
                session.add(band_charity)
                raise HTTPRedirect('index?id={}&message={}', band.id, 'Your charity decisions have been saved')

        return {
            'band': band,
            'message': message
        }

    def view_bio_pic(self, session, id):
        band = session.band(id)
        return serve_file(band.bio.pic_fpath, name=band.bio.pic_filename, content_type=band.bio.pic_content_type)

    def view_w9(self, session, id):
        band = session.band(id)
        return serve_file(band.taxes.w9_fpath, name=band.taxes.w9_filename, content_type=band.taxes.w9_content_type)

    def view_stage_plot(self, session, id):
        band = session.band(id)
        return serve_file(band.stage_plot.fpath, name=band.stage_plot.filename, content_type=band.stage_plot.content_type)
