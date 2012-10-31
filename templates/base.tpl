<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<HTML>
    <HEAD>
         <meta http-equiv="content-type" content="text/html; charset=UTF-8" >
         <link rel="stylesheet" type="text/css" href="css/main.css"> 
{% block head %}

{% endblock %}
    </HEAD>

    <BODY>
    
        
    
    
<div class="Content">
    
<div class="outer_layout">
<b class="xtop"><b class="xb1"></b><b class="xb2"></b><b class="xb3"></b><b class="xb4"></b></b>
<div class="xboxcontent">
    
<!-- ab hier alles umschliessende Box -->
      
      <menu class="Navigation">
          <li class="Bezeichner">ein Navigationsmenü </li>
          <li class="ListItem"><a href="/index">Startseite</a></li>
          <li class="ListItem"><a href="/">dummylink</a></li>
          <li class="ListItem"><a href="/">dummylink</a></li>
      </menu>


{% block content %}

{% endblock %}
</br>

<!-- bis hier alles umschliessende Box -->
</div>
<b class="xbottom"><b class="xb4"></b><b class="xb3"></b><b class="xb2"></b><b class="xb1"></b></b>
</div>
</div>
    </BODY>

</HTML>