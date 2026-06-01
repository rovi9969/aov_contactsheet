import re 
import nuke 


# Gather AOVS
def gather_aovs(node):
    read_node = node.input(0)
    if not read_node:
        nuke.message("No input connected. Please connect an EXR file.")
    else:    
        try:
            channels = read_node.channels()
        except ValueError:
            nuke.message("The connected node does not have any channels.")

        if len(channels) > 0:
            filtered_channels = []
            for c in channels:
                channel_name = c.split('.')[0]
                if 'crypto' in channel_name:
                    channel_name = re.sub(r'\d+$', '', channel_name)
                filtered_channels.append(channel_name)

            filtered_channels = sorted(set(filtered_channels))
            if not filtered_channels:
                nuke.message("No valid AOVs found after filtering.")
            else:
                knobs_to_remove = [knob for knob in node.knobs().keys() if knob.startswith("chk_") or knob == "AOVs"]
                for knob in knobs_to_remove:
                    if knob in node.knobs():
                        node.removeKnob(node[knob])

                for ch in filtered_channels:
                    knob_name = "chk_" + ch
                    if knob_name not in node.knobs():
                        knob = nuke.Boolean_Knob(knob_name, ch, True)
                        knob.setFlag(nuke.STARTLINE)
                        knob.setFlag(nuke.ALWAYS_SAVE)
                        node.addKnob(knob)
            
            print("AOVs gathered successfully! Now click 'Create ContactSheet'.")

# gather_aovs(nuke.thisNode())
            
# Create AOV Contactsheet

def _rgb_to_nuke_color(r, g, b, a=255):
    return (r << 24) | (g << 16) | (b << 8) | a

def _contactsheet_automatic_row_columns(read_node, contactsheet, num_connections):
    base_width = read_node.width()
    aspect_ratio = 16 / 9
    grid_cols = int((num_connections * aspect_ratio) ** 0.5)
    grid_rows = (num_connections // grid_cols) + (num_connections % grid_cols > 0)
    contactsheet_width = base_width * grid_cols
    contactsheet_height = int(contactsheet_width / aspect_ratio)

    contactsheet["width"].setValue(contactsheet_width)
    contactsheet["height"].setValue(contactsheet_height)
    contactsheet["rows"].setValue(grid_rows)
    contactsheet["columns"].setValue(grid_cols)
    contactsheet["roworder"].setValue("TopBottom")
    contactsheet["center"].setValue("TopBottom")

def create_aov_contactsheet(group):
    
    group.begin()
    for node in group.nodes():
        if node.Class() not in ["Input", "Output"]:
            nuke.delete(node)
    group.end()

    gathered_aovs = [knob.name().replace("chk_", "") for knob in group.knobs().values() if knob.name().startswith("chk_") and knob.value()]

    num_channels = len(gathered_aovs)

    if num_channels > 0:
        group.begin()
        input_node = nuke.toNode("Input1")
        if not input_node:
            input_node = nuke.createNode("Input")
            input_node.setName("Input1")

        read_node = input_node

        base_width = read_node.width()
        base_height = read_node.height()
        aspect_ratio = 16 / 9
        grid_cols = int((num_channels * aspect_ratio) ** 0.5)
        grid_rows = (num_channels // grid_cols) + (num_channels % grid_cols > 0)
        contactsheet_width = base_width * grid_cols
        contactsheet_height = int(contactsheet_width / aspect_ratio)

        dot1_node = nuke.createNode("Dot")
        dot1_node.setInput(0, read_node)

        dot2_node = nuke.createNode("Dot")
        dot2_node.setInput(0, dot1_node)

        mult1_node = nuke.createNode("Multiply")
        mult1_node.setInput(0, dot2_node)
        mult1_node["value"].setValue(0)

        add1_node = nuke.createNode("Add")
        add1_node.setInput(0, mult1_node)
        add1_node["value"].setValue([1] * 4)
        add1_node["value"].setExpression("parent.border_color.r", 0)
        add1_node["value"].setExpression("parent.border_color.g", 1)
        add1_node["value"].setExpression("parent.border_color.b", 2)
        add1_node["value"].setExpression("parent.border_color.a", 3)

        rectangle = nuke.createNode("Rectangle")
        rectangle.setInput(0, dot2_node)
        rectangle["area"].setExpression("parent.border_size", 0)
        rectangle["area"].setExpression("parent.border_size", 1)
        rectangle["area"].setExpression("width-area.x", 2)
        rectangle["area"].setExpression("height-area.x", 3)
        rectangle["replace"].setValue(True)
        rectangle["invert"].setValue(True)

        merge1_node = nuke.createNode("Merge2")
        merge1_node.setInput(0, add1_node)
        merge1_node.setInput(1, rectangle)
        merge1_node["operation"].setValue("multiply")

        contactsheet_node = nuke.createNode("ContactSheet")
        contactsheet_node.setInput(0, None)
        contactsheet_node.setName("AOV_ContactSheet")
        _contactsheet_automatic_row_columns( read_node, contactsheet_node, num_channels)
        '''
        contactsheet_node["width"].setValue(contactsheet_width)
        contactsheet_node["height"].setValue(contactsheet_height)
        contactsheet_node["rows"].setValue(grid_rows)
        contactsheet_node["columns"].setValue(grid_cols)
        contactsheet_node["roworder"].setValue("TopBottom")
        contactsheet_node["center"].setValue("TopBottom")
        '''

        reformat1_node = nuke.createNode("Reformat")
        reformat1_node.setInput(0, contactsheet_node)
        reformat1_node["type"].setValue("scale")
        reformat1_node["scale"].setExpression("parent.res_mult")

        dot3_node = nuke.createNode("Dot")
        dot3_node.setInput(0, reformat1_node)

        text_nodes = []
        
        for channel in gathered_aovs:
            if "crypto" in channel:
                cryptomatte_node = nuke.createNode("Cryptomatte")
                cryptomatte_node.setInput(0, dot1_node)
                cryptomatte_node["cryptoLayerChoice"].setValue(channel)
                cryptomatte_node.setName(f"Crypto_{channel}")            
                channel_node = cryptomatte_node
            else:
                shuffle = nuke.createNode("Shuffle")
                shuffle.setInput(0, dot1_node)
                shuffle["in"].setValue(channel)
                shuffle.setName(f"Shuffle_{channel}")
                channel_node = shuffle

            text_node = nuke.createNode("Text2")
            text_node.setInput(0, channel_node)
            text_node["message"].setValue(f"\n&emsp;&emsp;{channel}")
            text_node.setName(f"Text_{channel}")
            
            text_node["disable"].setExpression("!parent.show_labels")

            text_node["global_font_scale"].setExpression("parent.global_font_scale")  # Link global font scale

            text_node["color"].setValue([1] * 4)
            text_node["color"].setExpression("parent.font_color.r", 0)
            text_node["color"].setExpression("parent.font_color.g", 1)
            text_node["color"].setExpression("parent.font_color.b", 2)
            text_node["color"].setExpression("parent.font_color.a", 3)

            text_node["enable_background"].setExpression("parent.enable_label_bg")

            text_node["background_color"].setExpression("parent.label_bg_color.r", 0)
            text_node["background_color"].setExpression("parent.label_bg_color.g", 1)
            text_node["background_color"].setExpression("parent.label_bg_color.b", 2)
            text_node["background_color"].setExpression("parent.label_bg_color.a", 3)
            
            text_node["background_opacity"].setExpression("parent.label_bg_opacity")
        
            text_node["tile_color"].setValue(_rgb_to_nuke_color(0, 255, 255))


            '''
            text["opacity"].setExpression("parent.show_labels")
            text["size"].setExpression("50*parent.font_size_mult")
            text["color"].setValue([1] * 4)
            text["color"].setExpression("parent.font_color.r", 0)
            text["color"].setExpression("parent.font_color.g", 1)
            text["color"].setExpression("parent.font_color.b", 2)
            text["color"].setExpression("parent.font_color.a", 3)
            text["translate"].setExpression("parent.transform_X_knob", 0)
            text["translate"].setExpression("parent.transform_Y_knob", 1)
            text["font"].setValue("C:/Windows/Fonts/arial.ttf")
            '''
            
            merge2_node = nuke.createNode("Merge2")
            merge2_node.setInput(0, text_node)
            merge2_node.setInput(1, merge1_node)
            merge2_node["operation"].setValue("over")
            merge2_node["mix"].setExpression("parent.border_draw")
            
            text_nodes.append(merge2_node)

        for i, text_node in enumerate(text_nodes):
            contactsheet_node.setInput(i, text_node)

        output_node = nuke.toNode("Output1")
        if not output_node:
            output_node = nuke.createNode("Output")
            output_node.setName("Output1")
        output_node.setInput(0, dot3_node)

        group.end()
        nuke.message("ContactSheet created successfully!")
    else:
        nuke.message("EROR")

    group.end()

# create_aov_contactsheet(nuke.thisNode())

# Clear AOVs
def clear_aovs(group):
    group["aov_filter"].setValue(0)

    group.begin()
    for node in group.nodes():
        if node.Class() not in ["Input", "Output"]:
            nuke.delete(node)
    group.end()

    group.begin()
    knobs_to_remove = [knob for knob in group.knobs().keys() if knob.startswith("chk_") or knob == "AOVs"]
    for knob in knobs_to_remove:
        if knob in group.knobs():
            group.removeKnob(group[knob])
    group.end()
    print("AOV list cleared successfully! Group reset to default.")    

# clear_aovs(nuke.thisNode())

# knob changed
def _toggle_knobs(n, list_knobs, val):#, child_knobs_toggle):
    for knob in list_knobs:
        n[knob].setEnabled(val)

def knob_changed_script(node):
    # node = nuke.thisNode()
    knob = nuke.thisKnob()
    if knob.name() == "aov_filter":
        if knob.value() == "All":
            check_knobs = [knob for knob in node.knobs().keys() if knob.startswith('chk_')]
            if check_knobs:
                all_chk_knobs = [knob for knob in node.knobs().keys() if knob.startswith('chk_')]
                for chk_knob in all_chk_knobs:
                    node[chk_knob].setValue(False)
                for e_knob in check_knobs:
                    node[e_knob].setValue(True)
        if knob.value() == "AOV_Lights":
            T_AOV_Lights = ('chk_rgba', 'chk_RGBA')
            prefixes = T_AOV_Lights
            check_knobs = [knob for knob in node.knobs().keys() if knob.startswith(prefixes)]
            if check_knobs:
                all_chk_knobs = [knob for knob in node.knobs().keys() if knob.startswith('chk_')]
                for chk_knob in all_chk_knobs:
                    node[chk_knob].setValue(False)
                for e_knob in check_knobs:
                    node[e_knob].setValue(True)
        elif knob.value() == "AOV_Shaders":
            T_AOV_Shaders = ('_direct', '_indirect', 'chk_diffuse', 'chk_specular', 'chk_coat', 'chk_sheen', 'chk_transmission', 'chk_sss', 'chk_emission', 'chk_volume', 'albedo')
            substrings = T_AOV_Shaders
            check_knobs = [knob for knob in node.knobs() if isinstance(node[knob], nuke.Boolean_Knob) and any(sub in knob for sub in substrings)]
            if check_knobs:
                all_chk_knobs = [knob for knob in node.knobs().keys() if knob.startswith('chk_')]
                for chk_knob in all_chk_knobs:
                    node[chk_knob].setValue(False)
                for e_knob in check_knobs:
                    node[e_knob].setValue(True)
        elif knob.value() == "Tech":
            T_Tech_Passes = ('N', 'Z', 'P', 'motionvector', 'AO', 'Alpha', 'opacity', 'shw', 'shadow', 'crypto')
            substrings = T_Tech_Passes
            check_knobs = [knob for knob in node.knobs() if isinstance(node[knob], nuke.Boolean_Knob) and any(sub in knob for sub in substrings)]
            if check_knobs:
                all_chk_knobs = [knob for knob in node.knobs().keys() if knob.startswith('chk_')]
                for chk_knob in all_chk_knobs:
                    node[chk_knob].setValue(False)
                for e_knob in check_knobs:
                    node[e_knob].setValue(True)
        elif knob.value() == "-":
            all_chk_knobs = [knob for knob in node.knobs().keys() if knob.startswith('chk_')]
            for chk_knob in all_chk_knobs:
                node[chk_knob].setValue(False)
        else:
            pass

    # =================== on off parameters related to text labels and border outline ====================
    # knob = nuke.thisKnob()
    # --- ADD THIS BLOCK FIRST ---
    # Save checkbox states whenever one is toggled
    show_labels_parm = "show_labels"
    enable_label_bg_parm = "enable_label_bg"
    border_draw_parm = "border_draw"
    
    text_knobs = ["expression_label", "global_font_scale", "translate", "translate_btn", "font_color", "enable_label_bg", "label_bg_color", "label_bg_opacity" ]
    bg_nodes = ["label_bg_color", "label_bg_opacity"]

    if knob.name() == show_labels_parm:
        if knob.value() is True and node[enable_label_bg_parm].value() == True:
            _toggle_knobs(node, text_knobs, True)
        else:
            if knob.value() is True:
                [text_knobs.remove(x) for x in bg_nodes]
                #text_knobs.remove(enable_label_bg_parm)
                _toggle_knobs(node, text_knobs, True)
            else:
                _toggle_knobs(node, text_knobs, False)
        
        
    if knob.name() == enable_label_bg_parm:
        if knob.value() is True:
            _toggle_knobs(node, bg_nodes, True)
        if knob.value() is False:
            _toggle_knobs(node, bg_nodes, False)
            
    border_knobs = ["border_color", "border_size"]
    if knob.name() == border_draw_parm:
        if knob.value() is True:
            _toggle_knobs(node, border_knobs, True)
        else:
            _toggle_knobs(node, border_knobs, False)

# knob_changed_script(nuke.thisNode())

# onCreate
def restore_contactsheet_flags_script(group):
    flags_to_restore = {
        "res_mult": [nuke.NO_ANIMATION],
        "global_font_scale": [nuke.NO_ANIMATION],
        "translate": [nuke.NO_ANIMATION],
        "font_color": [nuke.NO_ANIMATION],
        "label_bg_color": [nuke.NO_ANIMATION],
        "label_bg_opacity": [nuke.NO_ANIMATION],
        "border_color": [nuke.NO_ANIMATION],
        "border_size": [nuke.NO_ANIMATION],

        "show_labels": [nuke.STARTLINE],
        "enable_label_bg": [nuke.STARTLINE],
        "border_draw": [nuke.STARTLINE],
        # Add more knobs here if needed
    }

    for knob_name, flag_list in flags_to_restore.items():
        k = group.knob(knob_name)
        if k:
            for flag in flag_list:
                k.setFlag(flag)
# restore_contactsheet_flags_script(nuke.thisNode())

############################################ translate_text_node
def translate_text_node(group):
    offset_x, offset_y = group["translate"].value()
    
    with group:
        # Get only Text2 nodes inside this group
        text_nodes = [n for n in group.nodes() if n.Class() == "Text2"]
        
        for text_node in text_nodes:
            knob = text_node["box"]
            
            # Force it to explicit values first (important!)
            text_node.forceValidate()
            
            # Get current box as list [left, bottom, right, top]
            box = knob.value()
            
            # If it's in auto/default mode (common values)
            if box[2] <= 0 or box[3] <= 0:  # right or top is negative/zero
                # Make it explicit by setting to current format or input size
                fmt = text_node.format()  # or get from input if connected  nuke.root()
                box = [0, 0, fmt.width(), fmt.height()]
                knob.setValue(box)
                text_node.forceValidate()
            
            # Now safely apply offset
            l = box[0] + offset_x
            b = box[1] + offset_y
            r = box[2] + offset_x
            t = box[3] + offset_y
            
            knob.setValue([l, b, r, t])
            text_node.forceValidate()
            
# translate_text_node(group.thisNode())

def toggle_channel_script(group):
    affect_channels_value = group["affect_channels"].value()
    channel_filter_values = group["channel_filter"].value().replace(" ", "").split(',')
    aovs_knob = [knob for knob in group.knobs().keys() if knob.startswith("chk_")]

    for channel_filter_value in channel_filter_values:
        channel_list = [x for x in aovs_knob if channel_filter_value in x]
        for channel_name in channel_list:
            group[channel_name].setValue(affect_channels_value)

# toggle_channel_script(nuke.thisNode())