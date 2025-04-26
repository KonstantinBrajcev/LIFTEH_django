import base64

encoded_str = "AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBPmx/7nZxL8lq2wwUFFAaUxPE6hv33BP3w0RDif6D8D+cxiGXIG6k8I19SvsX9gPwqRsJHOK0UgApN7tv/LZb/4="
decoded_bytes = base64.b64decode(encoded_str)
# decoded_str = decoded_bytes.decode('utf-8')
print(decoded_bytes)
