angular.module 'app', ['ngSanitize']

.controller 'RootController', ['$scope', '$sce', '$http', '$interval', 'util', ($scope, $sce, $http, $interval, util)->

  $scan_progress_bar = $('#scan_progress_bar')
  $scan_progress_bar.progress()

  $scope.app =
    name: 'NetEasy Music Player'
    title: 'NetEasy'
    copyright: $sce.trustAsHtml('This web application was created by ' +
      '<a href="https://github.com/tjumyk" target="_blank">Kelvin Miao</a>.<br>' +
      'Copyrights of the music files and music meta data belong to <a target="_blank" href="http://music.163.com">网易云音乐</a>.')

  $scope.scan = ->
    $scope.scanning = true
    $scope.scan_progress = undefined
    $scope.error = undefined
    $scope.music_list = undefined

    int = $interval ->
      if not $scope.scanning  # use local flag
        $interval.cancel(int)
        return
      $http.get '/api/status'
      .then (response)->
        status = response.data
        $scope.scan_progress =
          total: status.scan_total
          completed: status.scan_completed
    , 1000

    $http.get '/api/scan'
    .then (response)->
      $scope.scanning = false
      $scope.music_list = response.data
    , (response)->
      $scope.scanning = false
      $scope.error = util.formatResponseError(response)

  $scope.get_list = ->
    $scope.loading = true
    $scope.error = undefined
    $scope.music_list = undefined

    $http.get '/api/list'
    .then (response)->
      $scope.loading = false
      $scope.music_list = response.data
    , (response)->
      $scope.loading = false
      $scope.error = util.formatResponseError(response)

  $scope.time_to_now = (time)->
    return moment.unix(time).toNow()

  $scope.play_music = (music)->
    if $scope.player
      $scope.player.stop()
    $scope.player = AV.Player.fromURL("/file/#{music.mid}")
    $scope.player.play()

  $scope.$watch 'scan_progress.total', (total)->
    total = total or 0
    $scan_progress_bar.progress('set total', total)

  $scope.$watch 'scan_progress.completed', (completed)->
    completed = completed or 0
    $scan_progress_bar.progress('set progress', completed)

  $http.get '/api/status'
  .then (response)->
    status = response.data
    if status.never_scan
      $scope.scan()
    else
      if status.scanning
        $scope.scanning = true
        $scope.scan_progress =
          total: status.scan_total
          completed: status.scan_completed
        int = $interval ->
          $http.get '/api/status'
          .then (response)->
            status = response.data
            $scope.scan_progress =
              total: status.scan_total
              completed: status.scan_completed
            if not status.scanning  # use remote flag
              $interval.cancel(int)
              $scope.get_list()
        , 1000
      else
        $scope.get_list()
]
