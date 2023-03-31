#version 330

uniform mat4 prog;
uniform mat4 cam;
uniform mat4 trans;
uniform mat4 lookat;

in vec3 in_vert;
in vec3 normal ;
in vec2 text_cord;


out vec3 FragPos;
out vec3 Normal;
out vec2 v_tex_coord;



void main() {

    gl_Position =  prog* cam*lookat* trans* vec4(in_vert, 1.0);
    FragPos = vec3(trans * vec4(in_vert, 1.0f));
    Normal =  normal;
    v_tex_coord = text_cord;

}
