# search.cgi

This CGI enhanced the Nagios default search function provided by status.cgi that can only search hosts.

With search.cgi, now you can use regular expressions to match either hosts or services.

Installation instructions:

1. Put search.cgi in path nagios/sbin.

2. Add the following codes to anywhere you like in nagios/share/side.php:
```
<div class="navbarsearch"> 
<form method="get" action="<?php echo $cfg["cgi_base_url"];?>/search.cgi" target="<?php echo $link_target;?>"> 
<fieldset> 
<legend>Host Search:</legend> 
<input type='hidden' name='search' value='host'> 
<input type='text' name='host' size='15' class="NavBarSearchItem"> 
</fieldset> 
</form> 
</div> 

<div class="navbarsearch"> 
<form method="get" action="<?php echo $cfg["cgi_base_url"];?>/search.cgi" target="<?php echo $link_target;?>"> 
<fieldset> 
<legend>Service Search:</legend> 
<input type='hidden' name='search' value='service'> 
<input type='text' name='host' size='15' class="NavBarSearchItem"> 
</fieldset> 
</form> 
</div>
```
