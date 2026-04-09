# - name: Debug de parámetros de pool members
#   debug:
#     msg:
#       pool: "{{ f5_pool }}"
#       partition: "{{ f5_partition }}"
#       name: "{{ item.name.split(':')[0] }}"
#       port: "{{ item.name.split(':')[1] }}"
#       address: "{{ item.address }}"
#       state: "{{ f5_action }}"
#   loop: "{{ members_to_act }}"