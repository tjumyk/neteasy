angular.module('app').factory 'util', [->
  service =
    formatResponseError: (response)->
      if !!response.data and !!response.data.error
        return response.data.error
      else if response.status == -1
        return "Connection Aborted!"
      else
        return '[' + response.status + '] ' + response.statusText

    formatDate: (dateString)->
      return moment(dateString).format('LLL')

    prettyJSON: (json)->
      JSON.stringify(eval(json), null, 4)

    textToHTML: (text)->
      return $('<div>').text(text).html()

  return service
]
