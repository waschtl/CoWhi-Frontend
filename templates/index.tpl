{% extends "base.tpl" %}

{% block head %}
        <TITLE>
            Testseite
        </TITLE>
{% endblock head %}


{% block content %}
<p>eine Kleine Testseite zum Daten senden</p>

{% if data %}
<p> 
${data}
</p>
{% endif %}

<form class="forminput" action="index" method="post">
  <table border="0">
    <tr>
      <td>
        <label class="descr">Daten</label>
      </td>
      <td>
        <input class="inputfield" type="Post" name="data" ><br>
      </td>
    </tr>
    <tr>
      <td>
      </td>
      <td>
        <input type="submit" value="senden">
      </td>
    </tr>
  </table>
</form>

{% endblock content%}

