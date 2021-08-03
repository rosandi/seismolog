/*------------------------------
 * SeismoLog User Application
 * 
 * (c) 2021, Rosandi
 * 
 * User interface script to be sent to client
 *
 * rosandi@geophys.unpad.ac.id
 * 
*/

const ww= window.innerWidth;
const wh= window.innerHeight;

var runid;
var running=false;
var msrlen=100;
var avg=10;
var dt=1;
var chn=1;

var pline = [{x: [0],y: [0],type: 'scatter',name: 'V1'}, 
             {x: [0],y: [0],type: 'scatter',name: 'V2'},
             {x: [0],y: [0],type: 'scatter',name: 'V3'}];

plotwidth=0.55*ww;
plotheight=0.3*wh;

var layoutx = {
  width: plotwidth,
  height: plotheight,
  autosize: false,
  margin: {
    l: 50,
    r: 50,
    b: 50,
    t: 40,
    pad: 4
  },
  yaxis: {range: [-200, 200],autorange: true,title: 'X (a.u.)'},
  xaxis: {title: 'time (s)'}
};

var layouty = {
  width: plotwidth,
  height: plotheight,
  autosize: false,
  margin: {
    l: 50,
    r: 50,
    b: 50,
    t: 40,
    pad: 4
  },
  yaxis: {range: [-200, 200],autorange: true,title: 'Y (a.u.)'},
  xaxis: {title: 'time (s)'}
};

var layoutz = {
  width: plotwidth,
  height: plotheight,
  autosize: false,
  margin: {
    l: 50,
    r: 50,
    b: 50,
    t: 40,
    pad: 4
  },
  yaxis: {range: [-200, 200],autorange: true,title: 'Z (a.u.)'},
  xaxis: {title: 'time (s)'}
};

var plotdatax=[pline[0]];
var plotdatay=[pline[1]];
var plotdataz=[pline[2]];

Plotly.newPlot('plotareax',plotdatax,layoutx);
Plotly.newPlot('plotareay',plotdatay,layouty);
Plotly.newPlot('plotareaz',plotdataz,layoutz);

function getval(elid) {
    return document.getElementById(elid).value;
}

function setval(elid,val) {
    document.getElementById(elid).value=val;
}

function getstatus() {
    $.getJSON('status', function(stat) {
        if(stat.status) {
            $('#statustext').append('Logging daemon is <strong>running</strong><br>');
        } else {
            $('#statustext').append('Logging daemon is <strong>not running</strong><br>');
        }
        ss='Uptime: '+stat.uptime+'<br>Storage:<br>'
        sh=stat.disk[0].replace(/\s+/g, ' ').trim().split(' ');
        sc=stat.disk[1].replace(/\s+/g, ' ').trim().split(' ');
        dtab='<table style="margin-left: 0;width:13em"><tr><th class="noborder">'+sh[0]+
              '</th><th class="noborder">'+sh[1]+
             '</th><th class="noborder">'+sh[2]+
             '</th><th class="noborder">'+sh[3]+
             '</th></tr>';

        dtab+='<tr><td class="noborder">'+sc[0]+
              '</td><td class="noborder">'+sc[1]+
              '</td><td class="noborder">'+sc[2]+
              '</td><td class="noborder">'+sc[3]+
              '</td></tr></table>';
        
        $('#statustext').append(ss+dtab+'<br>');
        $('#statustext').append(stat.sens.replace(/\n/g,'<br>'))
        $('#statustext').append('<br>');
        
        $.getJSON('list/json/count', function(s){
            $('#statustext').append('Recorded data: '+s.count+'<br>');
        });
    });
    $('#statustext').scrollTop = $('#statustext').scrollHeight - $('#statustext').clientHeight;
}

function shutdown() {
    $("#statustext").html("<div style='text-align:center'>system shutdown...<br><H1>GOOD BYE...</H1></div>");
    $.getJSON("shutdown",function(st){});
}

function togglerun() {
    $.getJSON('status',
    function(stat){
        if(stat.status) {
            $.getJSON('stop',function(s){
                console.log('stopping');
                $('#runbtn').css({'background-color':'green'});
                $('#runbtn').html('START');
                var d=new Date();
                sdate='stop: '+d.getDate()+'-'+(d.getMonth()+1)+'-'+d.getFullYear();
                sdate+=' '+d.getHours()+':'+d.getMinutes()+':'+d.getSeconds()+'<br>';
                $('#statustext').append('<strong>'+sdate+'</strong>')
            });
        } else {
            $.getJSON('start',function(s){
                console.log('starting');
                $('#runbtn').css({'background-color':'red'});
                $('#runbtn').html('STOP');
                var d=new Date();
                sdate='start logging at: '+d.getDate()+'-'+(d.getMonth()+1)+'-'+d.getFullYear();
                sdate+=' '+d.getHours()+':'+d.getMinutes()+':'+d.getSeconds()+'<br>';
                $('#statustext').append('<strong>'+sdate+'</strong>');
                $('#statustext').append(s.program+'<br>');
            });
        }
    });
}

function listFiles(){
    $.getJSON('list/json',function(lst) {
        s='';
        for(i=0;i<lst.files.length;i++) {
            fl=lst.files[i].replace(/.json/,'')
            s+='<tr><td class="cell" onclick=plotfile($(this).html()+".json")>'+fl+'</td></tr>';
        }
        $('#filelist').html(s);
    });
}

function plotfile(fname) {
    if(fname=='--' || fname=='' || fname=='null') return;
    
    $.getJSON('load/'+fname, function(data){
        t=new Array(data.length);
        dt=data.tsample/data.length;
        for (i=0;i<data.length;i++) {
            t[i]=i*dt;
        }
        
        layoutx.xaxis={range: [0,data.tsample],title: 'time (s)'};
        layouty.xaxis={range: [0,data.tsample],title: 'time (s)'};
        layoutz.xaxis={range: [0,data.tsample],title: 'time (s)'};
        
        pline[0].x=t;
        pline[1].x=t;
        pline[2].x=t;
        
        pline[0].y=data.data[0];
        pline[1].y=data.data[1];
        pline[2].y=data.data[2];
        
        Plotly.redraw('plotareax');
        Plotly.redraw('plotareay');
        Plotly.redraw('plotareaz');
        $('#display').html('FILE: '+fname.replace(/.json/,''));
    });
    
}

function upload() {
    fname=$('#display').html().replace(/FILE: /,'')+'.json';
    $.getJSON('load/'+fname, function(data){
        sd=JSON.stringify(data);
        $.post('https://dock.unpad.ac.id/seismo/databox.php',
            {name: fname, json: sd},
            function(d,st) {
            console.log('respons:',d);
            console.log(st);
        });
    });
}

function apply() {
    msrlen=getval('len');
    avg=getval('avg');
    dt=getval('dt');
    vgain=getval('gain');   
    sconf='par/gain='+vgain+':stime='+msrlen+':avg='+avg+':dt='+dt+'/';
    $('#applybtn').css({'background-color':'#555'});
    setdirty=false;
    $.get(sconf,function(resp){
        $('#statustext').append(resp+'<br>');
    });
}

// Called on load
$.getJSON('get/settings', function(st){
    $('#statustexte').html('device settings:<br>'+JSON.stringify(st)+'<br>');
    $('#len').val(st.stime);
    $('#v_len').html(st.stime);
    $('#gain').val(st.gain);
    $('#v_gain').html(st.gain);
    $('#avg').val(st.avg);
    $('#v_avg').html(st.avg);
    $('#dt').val(st.dt);
    $('#v_dt').html(st.dt);
});

$.getJSON('status', function(s) {
   
    if(s.status) {
        $('#runbtn').css({'background-color':'red'});
        $('#runbtn').html('STOP');
    } else {
        dd=new Date();
        // Javascript starts month at 0 (January), funny heh?
        sd =dd.getFullYear()+'-'+(dd.getMonth()+1)+'-'+dd.getDate()+'+';
        sd+=dd.getHours()+':'+dd.getMinutes()+':'+dd.getSeconds();
        $.get('set/date='+sd,function(rs) {
            $('#statustext').html(rs+'<br>');
        });
    }
});
