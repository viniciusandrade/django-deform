from django.shortcuts import render
from urlparse import parse_qsl
import colander
import deform
from deform.exception import ValidationFailure
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_deform(request):
    class NameAndTitle(colander.Schema):
        name = colander.SchemaNode(colander.String())
        title = colander.SchemaNode(colander.String())
    class NamesAndTitles(colander.SequenceSchema):
        name_and_title = NameAndTitle(title='Name and Title')
    class NamesAndTitlesSequences(colander.SequenceSchema):
        names_and_titles = NamesAndTitles(title='Names and Titles')
    class Schema(colander.Schema):
        names_and_titles_sequence = NamesAndTitlesSequences(
            title='Sequence of Sequences of Names and Titles')
    schema = Schema()
    form = deform.Form(schema, buttons=('submit',))
    outer = form['names_and_titles_sequence']
    outer.widget = deform.widget.SequenceWidget(min_len=1, orderable=True)
    outer['names_and_titles'].widget = deform.widget.SequenceWidget(
        min_len=1, orderable=True)
        
    if request.method == 'GET':        
        rendered = form.render()
    if request.method == 'POST':
        # Here is our hack from above
        controls = parse_qsl(request.body, keep_blank_values=True)
        try:
            # If all goes well, deform returns a simple python structure of
            # the data. You use this same structure to populate a form with
            # data from permanent storage
            appstruct = form.validate(controls)            
        except ValidationFailure, e:
            # The exception contains a reference to the form object
            rendered = e.render()
        else:
            # See how I am populating it with the appstruct
            rendered = form.render(appstruct)


    # Deform will do you the courtesy of telling you which dependencies it
    # needs. Be sure to copy the files from the deform directory to the media
    # directory of your server
    return render_to_response('deform.html', {
        'form': rendered,
        'deform_dependencies': form.get_widget_resources()
    })


