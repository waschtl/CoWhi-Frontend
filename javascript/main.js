/*
 * Main.js
 * Javascript für die Interaktion mit dem Bottle-Server für CoWhi
 * 
 * TODO: - Sinnvolles aufteilen von Funktionen in verschiedene Dateien?
 *       
 */    

// globale Variablen ablegen

    // Popup mit aktuellem Auftrag einblenden
var jobPopup  = new Ext.Panel({
    id         :'jobPanel',
    floating   : true,
    modal      : true,
    centered   : true,
    width      : 300,
    height     : 300,
    styleHtmlContent: true,
    scroll     : 'vertical',
    html       : 'kein Auftrag',
    dockedItems: [{
        id   : 'jobPopupHtml',
        dock : 'top',
        xtype: 'toolbar',
        title: 'Aktueller Job'
    }]
});



	//Popup zum erstellen von eigenen Rezepten
	//TODO: später mal ermöglichen eigene Rezpete auf diese Art abzuspeichern...
var recipePanel = new Ext.Panel({
	id			: 'recipePanel',
	floating   : true,
    modal      : true,
    centered   : true,
    width      : 500,
    height     : 300,
    styleHtmlContent: true,
    scroll     : 'vertical',
    dockedItems: [{
    	dock  : 'top',
    	xtype : 'toolbar',
    	title : 'Eigenes Rezept'
    }, {
    	xtype : 'checkboxfield',
    	name  : 'checkboxCola',
    	label : 'Cola hinzufügen?',
    	checked : 'false',
    	listeners: {
    		check  : function(){
    			Ext.getCmp('spinnerfieldCola').enable();
    		},
    		uncheck: function(){
    			Ext.getCmp('spinnerfieldCola').disable();
    		}
    	}
    }, {
		xtype    : 'spinnerfield',
    	id       : 'spinnerfieldCola',
    	name     : 'cola',
    	title    : 'Cola',
    	value    : '1',
    	minValue: 0,
    	maxValue: 10,
    	disabled : 'true'
    }, {
    	xtype : 'checkboxfield',
    	name  : 'checkboxWhisky',
    	label : 'Whisky hinzufügen?',
    	checked : 'false',
    	listeners: {
    		check  : function(){
    			Ext.getCmp('spinnerfieldWhisky').enable();
    		},
    		uncheck: function(){
    			Ext.getCmp('spinnerfieldWhisky').disable();
    		}
    	}
    }, {
		xtype    : 'spinnerfield',
    	id       : 'spinnerfieldWhisky',
    	name     : 'Whisky',
    	title    : 'Whisky',
    	value    : '1',
    	minValue : 0,
    	maxValue : 10,
    	disabled : 'true'
    }, {
    	xtype    : 'button',
    	text     : 'Auftrag senden',
    	handler  : function(b, e){
    					Ext.getCmp('recipePanel').hide()
    					if (Ext.getCmp('spinnerfieldWhisky').disabled){
    						valWhisky = 0
    					} else {
    						valWhisky = Ext.getCmp('spinnerfieldWhisky').value
    					}
    					if (Ext.getCmp('spinnerfieldCola').disabled){
    						valCola = 0
    					} else {
    						valCola = Ext.getCmp('spinnerfieldCola').value
    					}
    					
                   		recipe = {name: 'eigenes Rezept',
								  whisky: valWhisky,
							      cola  : valCola};
						console.log(recipe)	      
						
						Ext.Msg.confirm('Sicherheitsabfrage',
            							'soll selbst erstelltes Rezept gemischt werden?',
            							 function(text){
            							 	console.log(text);
            							 	if (text == 'yes'){
            							 		sendOrder(recipe);	
            							 	}
            							 });
                   }
    }
    ]
    
})

    //Popup zum Position anfahren des Schlittens
var setSkidPopup = new Ext.Panel({
    id         :'skidPanel',
    floating   : true,
    modal      : true,
    centered   : true,
    width      : 600,
    height     : 300,
    styleHtmlContent: true,
    scroll     : 'vertical',
    dockedItems: [{
        id   : 'jobPopupHtml',
        dock : 'top',
        xtype: 'toolbar',
        title: 'neue Schlittenposition'
    }],
    items: [{
        id    : 'skidSlider',
        xtype : 'sliderfield',
        name  : 'postion',
        label : 'position',
        value : 200,
        minValue: 230,
        maxValue: 850,
        listeners:{
            dragend: function(slider, thumb, newValue){
                console.log(newValue)
                Ext.Ajax.request({
                    url: 'ajax/set_skid',
                    method: 'POST',
                    params: {'newPos': newValue}
                })
            }
        }
    }]
});
        
        // Statuspanel mit Buttons einblenden
var statusPanel = new Ext.Panel({
    id          : 'statusPanel',
    dockedItems : [
        {
            xtype: 'toolbar',
            dock : 'top',
            ui : 'light',
            items: [{
                id     : 'buttonJobs',
                //dock   : 'left',
                text   : 'x Aufträge in Liste',
                handler: function(b, e){
                    jobPopup.show('pop');
                }
            },{
                id     : 'buttonSkidPos',
                //dock   : 'left',
                text   : 'Schlittenposition ändern &nbsp &nbsp &nbsp',
                handler: function(b, e){
                    setSkidPopup.show('pop');
                }
        	},{
                id     : 'buttonRecipe',
                text   : 'neues Rezept',
                handler: function(b, e){
                    recipePanel.show('pop');
                }
            },{
            	id	   : 'buttonStartPos',
            	text   : 'Startposition anfahren',
            	handler: function(b, e){
            			 	Ext.Msg.confirm('Sicherheitsabfrage',
            								'soll Schlitten in Startpositin gefahren werden?',
        									function(text){
        							 			console.log(text);
        							 			if (text == 'yes'){
        							 				setStartPos();	
    							 				}
            								});
            							 
            			}
            }]
        }
    ]
})  


/*
 * Schlitten in Startposition fahren
 */
function setStartPos(){	 
	Ext.Ajax.request({
	    url: 'ajax/set_start_pos',
	    method: 'GET',
	    success: function(response, opts){
	    	console.log('success - Server responsed:');
	    	console.log(response.responseText);
	    }
    })	
}


/*
 * Jobliste von Server neu laden und Daten in Dokument eintragen
 */
function loadStates(){
    Ext.Ajax.request({
        url: 'ajax/get_state',
        reader: 'json',
        success: function(response, opts){
            var data = Ext.util.JSON.decode(response.responseText)
            Ext.getCmp('buttonJobs').setText(data.jobString);
            Ext.getCmp('jobPanel').update( data.activeJob)
            Ext.getCmp('buttonSkidPos').setBadge(data.skidPos);
        }
    })
}

/*
 * Einen Auftrag für eine Bestellung an den Server per AjaxRequest senden
 */
function sendOrder(recipe){
    Ext.Ajax.request({
        url: 'ajax/set_order',
        method: 'POST',
        params: recipe
        })
}

/*
 * starten Hauptprogramm
 */
Ext.setup({
    onReady: function(){
        console.log("starte SenchaTouch");
        var panel = new Ext.Panel({
            fullscreen: true,
            layout    : {
                        type : 'hbox',
                        pack : 'center',
                    },
            dockedItems: [{
                dock: 'top',
                xtype: 'toolbar',
                ui: 'dark',
                title: 'Prototyp CoWhi interface'
                }, 
                statusPanel
            ],
            
            items: [
                new Ext.Button({
                    id : 'textButton',
                    ui : 'decline',
                    text: 'Cola Whisky',
                    height : 200,
                    width  : 190,
                    style : {
                        backgroundImage: 'url(image/ice_in_whisky.jpg)'
                    },
                    handler: function(){
                        recipe = {name: 'Whisky pur',
								  whisky: 1,
							      cola  : 4};
							      
                        Ext.Msg.confirm('Sicherheitsabfrage',
            							'soll Cola Whisky gemischt werden?',
            							 function(text){
            							 	console.log(text);
            							 	if (text == 'yes'){
            							 		sendOrder(recipe);	
            							 	}
            							 });
                    }
                }),
                new Ext.Button({
                    ui  : 'decline',
                    text: 'Whisky pur',
                    height : 200,
                    width  : 190,
                    style : {
                        backgroundImage: 'url(image/whisky.jpg)'
                    },
                    handler: function (){
                    	recipe = {name: 'Whisky pur',
								  whisky: 1,
							      cola  : 0};
                        Ext.Msg.confirm('Sicherheitsabfrage',
            							'soll Whisky pur gemischt werden?',
            							 function(text){
            							 	console.log(text);
            							 	if (text == 'yes'){
            							 		sendOrder(recipe);	
            							 	}
            							 });
                    }
                })

            ]
        });
        
        //regelmäßig die Jobliste aktualisieren
        window.setInterval("loadStates()", 5000);  
    }
    
})


    