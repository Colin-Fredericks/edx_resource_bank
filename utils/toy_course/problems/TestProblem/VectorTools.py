from __future__ import division

direction = random.choice(["+z","-z","+y","-y","+x","-x"])

def dir2vec(dir):

	translator = {
		"+x" : [1,0,0],
		"-x" : [-1,0,0],
		"+y" : [0,1,0],
		"-y" : [0,-1,0],
		"+z" : [0,0,1],
		"-z" : [0,0,-1]
	}
	
	return translator[dir]


def vec2dir(vec):

	translator = {
		[1,0,0] : "+x",
		[-1,0,0] : "-x",
		[0,1,0] : "+y",
		[0,-1,0] : "-y",
		[0,0,1] : "+z",
		[0,0,-1] : "-z"
	}
	
	return translator[vec]


def crossprod(vec1, vec2):
	def vec3 = [0,0,0]
	
	vec3[0] = vec1[1]*vec2[2] - vec1[2]*vec2[1]
	vec3[1] = vec1[0]*vec2[2] - vec1[2]*vec2[0]
	vec3[2] = vec1[0]*vec2[1] - vec1[1]*vec2[0]
	
	return vec3

def dotprod(vec1, vec2):

	return vec1[0]*vec2[0] + vec1[1]*vec2[1] + vec1[2]*vec2[2]