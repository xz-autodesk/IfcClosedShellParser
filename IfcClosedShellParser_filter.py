def parse_step_file(step_file_content):
    entities = {}
    for line in step_file_content.strip().split('\n'):
        if '=' in line:
            key, value = line.split('=')
            entities[key.strip()] = value.strip()

    def get_cartesian_point(cartesian_point_entity):
        if cartesian_point_entity.startswith('IFCCARTESIANPOINT'):
            coords = cartesian_point_entity.split('((')[1].strip('));').split(',')
            return tuple(map(float, coords))
        return ()

    def get_polyloop_points(polyloop_entity):
        if polyloop_entity.startswith('IFCPOLYLOOP'):
            point_refs = polyloop_entity.split('((')[1].strip('));').split(',')
            points = [get_cartesian_point(entities[ref.strip()]) for ref in point_refs]
            return points
        return []

    def get_face_points(face_entity):
        if face_entity.startswith('IFCFACE'):
            bounds_refs = face_entity.split('((')[1].strip('));').split(',')
            for bound_ref in bounds_refs:
                bound_ref = bound_ref.strip()
                outer_bound_entity = entities[bound_ref]
                if outer_bound_entity.startswith('IFCFACEOUTERBOUND'):
                    polyloop_ref = outer_bound_entity.split('(')[1].strip(');').split(',')[0]
                    polyloop_ref = polyloop_ref.strip()
                    return get_polyloop_points(entities[polyloop_ref])
        return []

    faces = {}
    for entity, value in entities.items():
        if value.startswith('IFCCLOSEDSHELL'):
            face_refs = value.split('((')[1].strip('));').split(',')
            for face_ref in face_refs:
                face_ref = face_ref.strip()
                faces[face_ref] = get_face_points(entities[face_ref])

    return faces

# STEP file content
step_file_content1 = '''
#2168011 = IFCCLOSEDSHELL((#2153192, #2153197));
#2153189 = IFCPOLYLOOP((#2153025, #2153003, #2152561));
#2153191 = IFCFACEOUTERBOUND(#2153189, .T.);
#2153192 = IFCFACE((#2153191));
#2153194 = IFCPOLYLOOP((#2152693, #2152675, #2152779));
#2153196 = IFCFACEOUTERBOUND(#2153194, .T.);
#2153197 = IFCFACE((#2153196));
#2153025 = IFCCARTESIANPOINT((49387.6928748742, 49.0952722359138, 862.679491924311));
#2153003 = IFCCARTESIANPOINT((49382.6928748742, 49.0952722359138, 862.679491924311));
#2152561 = IFCCARTESIANPOINT((49382.6928748742, 774.095272232708, 862.679491924298));
#2152693 = IFCCARTESIANPOINT((49387.6928748742, 779.095272232707, 862.679491924304));
#2152675 = IFCCARTESIANPOINT((49392.6928748742, 784.095272232715, 862.679491924311));
#2152779 = IFCCARTESIANPOINT((49397.6928748742, 789.095272232713, 862.679491924317));
'''

def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print("File not found. Please check the file path.")
        return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

def format_for_autocad_and_write_scr(faces_with_coordinates, output_file):
    filter_face = {}
    for face_id, points in faces_with_coordinates.items():
        isSmall = True
        for x, y, z in points:
            # if x < 3373.0 and y < 4718.0:
            # if x < 6573.0 and y < 8918.0:
            #if x < 8573.0 and y < 10918.0:
            if x < 11573.0 and y < 12918.0:
                continue
            isSmall = False
        if isSmall:
            filter_face[face_id] = points
            print(f"{face_id}", end =", ")
    with open(output_file, 'w') as file:
        for face_id, points in filter_face.items():
            command = "3DPOLY\n"
            for x, y, z in points:
                # Add each point to the command
                command += f"{x},{y},{z} "
            command += "c\n"  # 'c' to close the polyline
            file.write(command)     
        file.write("ZOOM E\n")  # Zoom extents
        
                

# Example usage
file_path = 'ifcclosedshell2.ifc'  # Replace with your file path
output_file = 'draw_faces_filter.scr'  # The output file name

step_file_content = read_file_content(file_path)

# Parse and get faces with coordinates
faces_with_coordinates = parse_step_file(step_file_content)
for face, points in faces_with_coordinates.items():
    print(f"{face}: {points}")

format_for_autocad_and_write_scr(faces_with_coordinates, output_file)
# print(f"AutoCAD script written to {output_file}")