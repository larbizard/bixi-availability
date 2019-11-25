//TODO: Import Google Maps NPM instead of using script in index.html

var vm = new Vue({
  el: '#search-bar',
  data: {
      markerCoordinates: [],
      selectedDay: 'Sunday',
      days: [
      { text: 'Sunday', value: 'W-SUN' },
      { text: 'Monday', value: 'W-MON' },
      { text: 'Tuesday', value: 'W-TUE' },
      { text: 'Wednesday', value: 'W-WED' },
      { text: 'Thursday', value: 'W-THU' },
      { text: 'Friday', value: 'W-FRI' },
      { text: 'Saturday', value: 'W-SAT' },
      ],
      hour: '14',
      short_name: '6043',
      server_path: 'https://www.bixi-availability.com/bixiOccupancy/',
      map: '',
      markers: []
  },
  mounted: function () {
  try{
    this.map = new google.maps.Map(document.getElementById('mapName'), {
          center: {lat: 45.509462, lng: -73.613413},
          zoom: 13
        });
        this.getStationMarkers();
        this.fetchData();
        var colors = this.generateColors(Array.apply(null, Array(24)).map(Number.prototype.valueOf,0));
        var ctx = document.getElementById('myChart').getContext('2d');
        var myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [...Array(24).keys()],
                datasets: [{
                    label: '# of Availability in %',
                    data: Array.apply(null, Array(24)).map(Number.prototype.valueOf,0),
                    backgroundColor: colors,
                    borderColor: colors,
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
        });
  }
  catch(e){
    alert(e);
  }
  },
  methods: {
  hideAllInfoWindows() {
   this.markers.forEach(function(marker) {
     marker.infowindow.close(this.map, marker);
  });
},
  getDayText(value){
    var dayName = '';
    this.days.forEach(function(day){
        if(value == day.value) {dayName = day.text};
    });
    return dayName;
  },
  getTheMostBusyStations(){
  /*Append the result to an area of the screen when ready
    this.markers.forEach(marker){
    };*/
  },
  getBikeIcon(availability){
    if(availability>80){
        return 'images/green-bike.png';
    }else if(availability>50){
       return 'images/yellow-bike.png';
    }else if(availability>25){
       return 'images/orange-bike.png';
    }else{
       return 'images/black-bike.png';
    }
  } ,

    fetchData() {
        var self = this;
        try{
            $.getJSON("stations_availability.json", function(json) {
                self.markers.forEach(function(marker){
                    availability = json[marker.station_data.short_name.toString()][self.selectedDay][self.hour]['availability'];
                    if(!availability){
                        marker.infowindow.setContent("<p style='font-size: 1.5vw'><img src='images/red-bike-no-back.png'/><br/>No data !</p>");
                    }else {
                        capacity = json[marker.station_data.short_name.toString()][self.selectedDay][self.hour]['capacity'];
                        marker.infowindow.setContent("<p style='font-size: 1.5vw'><img src='" + self.getBikeIcon(availability) + "'/><br/>At station <strong>"+ marker.title    +
                        "</strong><br/>on "+ self.getDayText(self.selectedDay) + "'s<br/>between <strong>" + self.hour.toString()  + ":00</strong> and <strong>" +
                        (Number(self.hour)+1).toString() + ":00</strong><br/><strong>"+availability.toString()+"%</strong> of bikes are available.<br/>An<strong> average of " + Math.floor(availability*capacity/100) + " out of " + capacity + " bikes.</strong></p>");
                        marker.setIcon(self.getBikeIcon(availability));
                    }
                });
            });
        }
        catch(e){
            alert(e);
        }

    },
    generateColors(availability){
        var colors = [];
        for(value in availability){
           if(availability[value]>80){
                colors.push('green');
            }else if(availability[value]>50){
               colors.push('yellow');
            }else if(availability[value]>25){
               colors.push('orange');
            }else{
               colors.push('black');
            }
        }
        return colors;
    },
    getStationMarkers() {
        try{
            var self = this;
            $.getJSON("station_information.json", function(json) {
                json['data']['stations'].forEach(function(station){
                      const position = new google.maps.LatLng(station.lat, station.lon);
                      var infowindow = new google.maps.InfoWindow({
                      });

                      const marker = new google.maps.Marker({
                        position : position,
                        map : self.map,
                        title : station.name,
                        icon : 'images/red-bike-no-back.png'
                      });
                      marker.station_data = station;
                      marker.addListener('click', function() {
                        self.hideAllInfoWindows();
                        marker.infowindow.open(this.map, marker);
                        $.getJSON("stations_availability.json", function(json) {
                            availability =  []
                            for(value in json[marker.station_data.short_name.toString()][self.selectedDay]){
                                availability.push(json[marker.station_data.short_name.toString()][self.selectedDay][value]['availability']);
                            };
                            var colors = self.generateColors(availability);
                            var ctx = document.getElementById('myChart').getContext('2d');
                            var myChart = new Chart(ctx, {
                                type: 'bar',
                                data: {
                                    labels: [...Array(24).keys()],
                                    datasets: [{
                                        label: '# of Availability in %',
                                        data: availability,
                                        backgroundColor: colors,
                                        borderColor: colors,
                                        borderWidth: 1
                                    }]
                                },
                                options: {
                                    scales: {
                                        yAxes: [{
                                            ticks: {
                                                beginAtZero: true
                                            }
                                        }]
                                    }
                                }
                            });
                        });
                      });
                      marker.infowindow = infowindow;
                      self.markers.push(marker);
                });
                });
        }
        catch(e) {
            alert(e);
        }
    }
  },
});

vm.selectedDay = 'W-SUN';
vm.day = 'W-SUN';