import nuke 

def contactsheet_group(node_name="AOV_Contactsheet"):
    group = nuke.createNode("Group")
    #group["disable_group_view"].setValue(True)
    group.setName(node_name)

    # ==================== Credits ==================================
    credit_knob = nuke.Text_Knob("credits", "")
    credit_knob.setValue("<br><font size=4 color=grey><b>rm_AOV_Contactsheet v1.1</b></font><br><font size=2 color=grey>created by <u>Ravi Motwani</u>.<br>published : June, 2026.</font>")
    group.addKnob(credit_knob)

    # Separator
    group.addKnob(nuke.Text_Knob("separator0", ""))

    # ==================== Resolution Multiplier ====================
    res_mult_knob = nuke.Double_Knob("res_mult", "Resolution Multiplier")
    group.addKnob(res_mult_knob)
    group["res_mult"].setValue(0.25)
    group["res_mult"].setRange(0, 5)
    res_mult_knob.setFlag(nuke.NO_ANIMATION)
    res_mult_knob.clearFlag(nuke.STARTLINE)  # Clear the STARTLINE flag to align with the label
    res_mult_knob.clearFlag(nuke.ENDLINE)
    res_mult_knob.setTooltip("Set the resolution multiplier for the contactsheet")

    # Separator
    group.addKnob(nuke.Text_Knob("separator1", ""))

    # ==================== Buttons ====================
    btn_gather_aovs = nuke.PyScript_Knob("gather_aovs_btn", "Gather AOVs")
    gather_aovs_call = '''import aov_contactsheet.logic as logic;
logic.gather_aovs(nuke.thisNode())
    '''
    btn_gather_aovs.setCommand(gather_aovs_call)
    group.addKnob(btn_gather_aovs)
    btn_gather_aovs.setTooltip("Gather's AOVs for the contactsheet")
    
    btn_create = nuke.PyScript_Knob("create_contactsheet_btn", "Create Contactsheet")
    create_layer_contactsheet_call = '''import aov_contactsheet.logic as logic;
logic.create_aov_contactsheet(nuke.thisNode())    
    '''
    btn_create.setCommand(create_layer_contactsheet_call) # create_pass_contactsheet_script
    group.addKnob(btn_create)
    btn_create.setTooltip("Create the contactsheet")

    btn_clear = nuke.PyScript_Knob("clear_btn", "Clear")
    btn_call = '''import aov_contactsheet.logic as logic; 
logic.clear_aovs(nuke.thisNode())
    '''
    btn_clear.setCommand(btn_call) # clear_script
    group.addKnob(btn_clear)
    btn_clear.setTooltip("Clear the contactsheet")

    group.addKnob(nuke.Text_Knob("separator2", ""))

    # ==================== Text Labels Tab ====================
    text_label_tabin = nuke.Tab_Knob('text_groupin', 'T E X T   L A B E L S', nuke.TABBEGINCLOSEDGROUP)
    group.addKnob(text_label_tabin)
    text_label_tabin.clearFlag(nuke.STARTLINE)  # Clear the STARTLINE flag to align with the label

    show_label = nuke.Boolean_Knob("show_labels", "Show Labels")
    show_label.setValue(True)
    show_label.setFlag(nuke.STARTLINE)
    group.addKnob(show_label)
    show_label.setTooltip("Toggle to show or hide labels")

    # Expression Label (hidden)
    expr_knob = nuke.String_Knob("expression_label", "Label Expression")
    group.addKnob(expr_knob)
    expr_knob.setValue('[regsub {[\._]?\d+$} [file rootname [file tail [value [topnode parent ].file]]] ""]')
    expr_knob.setVisible(False)
    expr_knob.setTooltip("Expression to generate label text")

    # Global Font Scale
    font_scale_knob = nuke.Double_Knob("global_font_scale", "Global Font Scale")
    group.addKnob(font_scale_knob)
    group["global_font_scale"].setValue(1.0)
    font_scale_knob.setFlag(nuke.NO_ANIMATION)
    font_scale_knob.setTooltip("Set the global text font scale")

    # Translate (XY + Button)
    translate_knob = nuke.XY_Knob("translate", "Translate")
    translate_knob.setFlag(nuke.NO_ANIMATION)
    group.addKnob(translate_knob)
    translate_knob.setTooltip("Set the translation of the text labels")

    btn_translate = nuke.PyScript_Knob("translate_btn", "Apply")
    btn_translate.setCommand('''import aov_contactsheet.logic as logic; 
logic.translate_text_node(nuke.thisNode())''') # translate_text_node_script
    group.addKnob(btn_translate)
    btn_translate.setTooltip("Apply the translation to the text labels")

    # Font Color
    font_color_knob = nuke.AColor_Knob("font_color", "Font Color")
    group.addKnob(font_color_knob)
    group["font_color"].setValue([1.0, 1.0, 1.0, 1.0])
    font_color_knob.setFlag(nuke.NO_ANIMATION)
    font_color_knob.setTooltip("Change the text color")

    # Label Background
    enable_bg = nuke.Boolean_Knob("enable_label_bg", "Enable Label Background")
    enable_bg.setValue(True)
    enable_bg.setFlag(nuke.STARTLINE)
    group.addKnob(enable_bg)
    enable_bg.setTooltip("Toggle to enable or disable label background")

    # Background Color
    background_color_knob = nuke.AColor_Knob("label_bg_color", "Label Background Color")
    group.addKnob(background_color_knob)
    group["label_bg_color"].setValue([1.0, 1.0, 1.0, 1.0])
    background_color_knob.setFlag(nuke.NO_ANIMATION)
    background_color_knob.setTooltip("Set the label background color")

    # Background Opacity
    background_opacity_knob = nuke.Double_Knob("label_bg_opacity", "Label Background Opacity")
    group.addKnob(background_opacity_knob)
    group["label_bg_opacity"].setValue(0.1)
    background_opacity_knob.setFlag(nuke.NO_ANIMATION)
    background_opacity_knob.setTooltip("Set the label background opacity")

    tab_label_groupout = nuke.Tab_Knob('text_groupout', None, nuke.TABENDGROUP)
    group.addKnob(tab_label_groupout)
    tab_label_groupout.clearFlag(nuke.STARTLINE)
    group.addKnob(nuke.Text_Knob("separator3", "", " " * 20))

    

    # ==================== Border Tab ====================
    tab_border_tabin = nuke.Tab_Knob('border_begin', 'B O R D E R   O U T L I N E', nuke.TABBEGINCLOSEDGROUP)
    group.addKnob(tab_border_tabin) #
    tab_border_tabin.clearFlag(nuke.STARTLINE)  # Clear the STARTLINE flag to align with the label

    border_toggle = nuke.Boolean_Knob("border_draw", "Draw Border")
    border_toggle.setValue(True)
    border_toggle.setFlag(nuke.STARTLINE)
    group.addKnob(border_toggle)
    border_toggle.setTooltip("Toggle to draw or not draw the border")

    border_color = nuke.AColor_Knob("border_color", "Border Color")
    group.addKnob(border_color)
    group["border_color"].setValue([0.0, 0.5, 0.0, 1.0])
    border_color.setFlag(nuke.NO_ANIMATION)
    border_color.setTooltip("Set the border color")

    border_size = nuke.Double_Knob("border_size", "Border Size")
    group.addKnob(border_size)
    border_size.setRange(0, 20)
    border_size.setValue(10)
    border_size.setFlag(nuke.NO_ANIMATION)
    border_size.setTooltip("Set the border size")

    tab_border_groupout = nuke.Tab_Knob('border_out', None, nuke.TABENDGROUP)
    group.addKnob(tab_border_groupout)
    tab_border_groupout.clearFlag(nuke.STARTLINE)

    group.addKnob(nuke.Text_Knob("separator4", ""))
    
    dropdown_list = ["All", "AOV_Lights", "AOV_Shaders", "Tech", "-"]
    dropdown_preset = nuke.Enumeration_Knob("aov_filter", "Preset", dropdown_list)
    #dropdown_preset.setValues(dropdown_list)
    group.addKnob(dropdown_preset)
    dropdown_preset.setTooltip("Presets for AOVs selection in below list")

    channel_filter_knob = nuke.String_Knob("channel_filter", "channel filter :")
    group.addKnob(channel_filter_knob)
    channel_filter_knob.setTooltip( "add common text of aovs and separate using comma,/neg : direct,indirect,sss" )
    
    affect_channel_knob = nuke.Boolean_Knob("affect_channels", "affect channels")
    group.addKnob( affect_channel_knob )
    affect_channel_knob.setValue(True)
    affect_channel_knob.setTooltip( "Enabling this will enable items of below list, disabling will turn it off." )
    
    btn_toggle_channel = nuke.PyScript_Knob("toggle_channel_btn", "Toggle Channels")
    group.addKnob( btn_toggle_channel )
    t_channel_script = '''import aov_contactsheet.logic as logic; 
logic.toggle_channel_script(nuke.thisNode())'''
    btn_toggle_channel.setCommand(t_channel_script)

    
    group.addKnob(nuke.Text_Knob("separator5", ""))
    
    # ==================== Callbacks ====================
    toggle_knobChanged_knob = nuke.PyCustom_Knob("toggle_knobChanged", "")
    group.addKnob(toggle_knobChanged_knob)
    t_knobChanged_script = f"""nuke.thisNode().knob("knobChanged").setValue('import aov_contactsheet.logic as logic; logic.knob_changed_script(nuke.thisNode())')"""
    toggle_knobChanged_knob.setValue(t_knobChanged_script)

    # Restore flags on creation (this is the key part)
    on_create_knob = nuke.PyCustom_Knob("onCreate_1", "")
    group.addKnob(on_create_knob)
    onCreate_script = f"""nuke.thisNode().knob('onCreate').setValue('import aov_contactsheet.logic as logic;logic.restore_contactsheet_flags_script(nuke.thisNode())')"""
    on_create_knob.setValue(onCreate_script)

    # ===================== Input Output ===============================
    group.begin()
    nuke.createNode("Input")
    nuke.createNode("Output")
    group.end()
    return group


#contactsheet_group()