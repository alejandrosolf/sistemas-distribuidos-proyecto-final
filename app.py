import streamlit as st
import requests
import json

webhook_url = "https://hooks.slack.com/services/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"

def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def save_json(data):
    return json.dumps(data, indent=4)

def get_keys(json_dict):
    if isinstance(json_dict, dict):
        for k, v in json_dict.items():
            if isinstance(v, (int, str, list)):
                yield (k, v)
            else:
                yield from list(get_keys(v))
    elif isinstance(json_dict, dict):
        for o in json_dict:
            yield from list(get_keys(o))

def send_slack_message(json_data):
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(webhook_url, json={'text': str(json_data)}, headers=headers)
        
        if response.status_code == 200:
            st.success("Archivo JSON enviado a Slack correctamente")
        else:
            st.error(f"Error al enviar a Slack: {response.text}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
    

keys_value_modify = []
keys_list_modify = []

st.title("Modificar a json")

uploaded_file = st.file_uploader("Escoge un archivo", type="json")

if 'modified_data' not in st.session_state:
    st.session_state.modified_data = {}

if uploaded_file is not None:
    data = json.load(uploaded_file)

    if not st.session_state.modified_data:
        st.session_state.modified_data = data

    pairs_key_values = dict(get_keys(data))

    for key, value in pairs_key_values.items():
        if isinstance(value, list):
            for counter in range(len(value)):
                st.markdown(f"El contenido de {key} posicion {counter} es {str(value[counter])}")
                keys_list_modify.append([key, counter])
        else:
            st.markdown(f"El contenido de {key} es {str(value)}")
            keys_value_modify.append(key)

if len(keys_value_modify) > 0 and len(keys_list_modify) > 0:
    key_to_modify = st.selectbox(
    "¿Cual valor desea modificar?",
    keys_value_modify + keys_list_modify,
    )

    if isinstance(key_to_modify, list):
        new_value = st.text_input("Nuevo valor", value=pairs_key_values[key_to_modify[0]][key_to_modify[1]])
    else:
        new_value = st.text_input("Nuevo valor", value=pairs_key_values[key_to_modify])

    if st.button("Modificar"):
        if isinstance(key_to_modify, list):
            if key_to_modify[0] == "VPCZoneIdentifier":
                st.session_state.modified_data["myASG"]["Properties"]["VPCZoneIdentifier"][key_to_modify[1]] = new_value
            elif key_to_modify[0] == "Fn::GetAtt":
                st.session_state.modified_data["myASG"]["Properties"]["LaunchTemplate"]["Version"]["Fn::GetAtt"][key_to_modify[1]] = new_value
            st.success(f"Modificado '{key_to_modify[0]}' en posicion {key_to_modify[1]} a '{new_value}'")
        else:
            if key_to_modify == "Type":
                st.session_state.modified_data["myASG"]["Type"] = new_value
            elif key_to_modify == "Ref":
                st.session_state.modified_data["myASG"]["Properties"]["LaunchTemplate"]["LaunchTemplateId"]["Ref"] = new_value
            elif key_to_modify == "MaxSize":
                st.session_state.modified_data["myASG"]["Properties"]["MaxSize"] = new_value
            elif key_to_modify == "MinSize":
                st.session_state.modified_data["myASG"]["Properties"]["MinSize"] = new_value
            st.success(f"Modificado '{key_to_modify}' a '{new_value}'")

        st.write("Data modificada:")
        st.json(st.session_state.modified_data)

        modified_json = save_json(st.session_state.modified_data)

        st.download_button(
            label="Descargar nuevo archivo",
            data=modified_json,
            file_name="new_json_file.json",
            mime="application/json"
        )
    
    if st.button("Enviar a Slack"):
        try:
            payload = save_json(st.session_state.modified_data)
            send_slack_message(payload)
        except json.JSONDecodeError:
            st.error("Error: El JSON no es válido. Corrígelo e intenta nuevamente.")
