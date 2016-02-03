import bpy
from bpy.types import NodeTree, Node, NodeSocket
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

bpy.types.Scene.graphing = bpy.props.BoolProperty(default=False)

class GraphScene(bpy.types.Operator):
    """Add a simple box mesh"""
    bl_idname = "scene_nodes.graph_scene"
    bl_label = "Add Box"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        
        #Stops nodes from being deleted when nodes are cleared
        context.scene.graphing = True
        
        nodeGroup = bpy.data.node_groups['NodeTree']
        
        nodeGroup.nodes.clear()           


        for sceneIndex, scene in enumerate(bpy.data.scenes):
            
            newSceneNode = nodeGroup.nodes.new('SceneNodeType')
            newSceneNode.sceneIndex = sceneIndex
            newSceneNode.select = False
            newSceneNode.location[1] = sceneIndex * -newSceneNode.height
            
            #Only get objects that aren't children themselves
            totalHeight = len([object for object in scene.objects if object.parent == None]) * -110
            
            yOffset = 0
                                      
            for objectIndex, object in enumerate(scene.objects):
                
                newObjectNode = nodeGroup.nodes.new('ObjectNodeType')
                newObjectNode.objectIndex = objectIndex
                newObjectNode.scene = scene.name
                newObjectNode.select = False
                newObjectNode.name = scene.objects[objectIndex].name
                newObjectNode.use_custom_color = True
               
                #print("Correct: Looking on object "+object.name+", node "+newObjectNode.name)
                                
                objectType = scene.objects[objectIndex].type
                                
                if objectType == "MESH":
                    
                    newObjectNode.color = [1.000000, 0.792470, 0.552983]
                    
                    newObjectNode.outputs.new('NodeSocketFloat', "Material")
                    
                elif objectType == "LAMP":
                    
                    newObjectNode.color = [1.000000, 0.936002, 0.395156]
                                
                if scene.objects[objectIndex].parent == None:
                    
                    newObjectNode.location[1] = (yOffset * -140) - (totalHeight/2) + 12
                    newObjectNode.location[0] = newSceneNode.width + 80
                    
                    nodeGroup.links.new(newObjectNode.inputs[0], newSceneNode.outputs[0])  
                    
                    yOffset = yOffset + 1
                    
                else:
                    
                    parentName = scene.objects[objectIndex].parent.name
                    
                    if len(nodeGroup.nodes[parentName].outputs['Child'].links) == 0:
                        
                        newObjectNode.location[1] = nodeGroup.nodes[parentName].location[1]
                        
                    else:
                        
                        totalChildren = len(nodeGroup.nodes[parentName].outputs['Child'].links)
                        
                        lastChild = nodeGroup.nodes[parentName].outputs['Child'].links[totalChildren-1].to_node
                        
                        newObjectNode.location[1] = lastChild.location[1] - 140
                        
                    newObjectNode.location[0] = nodeGroup.nodes[parentName].location[0] + newObjectNode.width + 120
                    
                    nodeGroup.links.new(newObjectNode.inputs[0], nodeGroup.nodes[parentName].outputs[0])
                 
                
                for materialSlot in object.material_slots:
                    
                    #print("Looking on object "+object.name+", node "+newObjectNode.name)
                    
                    objectMaterial = materialSlot.material
                    
                    materialIndex = 0
                                        
                    for material in bpy.data.materials:
                        
                        if objectMaterial.name == material.name:
                                                        
                            #If material node doesn't already exist
                            if material.name not in nodeGroup.nodes:
                                                                                        
                                newMaterialNode = nodeGroup.nodes.new('MaterialNodeType')
                                newMaterialNode.materialIndex = materialIndex
                                newMaterialNode.select = False
                                newMaterialNode.location[1] = newObjectNode.location[1]
                                newMaterialNode.location[0] = newObjectNode.location[0] + newObjectNode.width + 120
                                newMaterialNode.name = bpy.data.materials[materialIndex].name                                
                                newMaterialNode.use_custom_color = True                   
                                newMaterialNode.color = [1.000000, 0.608448, 0.993887] 
                            
                                input = newMaterialNode.inputs[0]
                                                    
                            else:
                                
                                input = nodeGroup.nodes[bpy.data.materials[materialIndex].name].inputs.new('NodeSocketFloat', "Object")

                        materialIndex+=1                    
                    
                        print(newObjectNode.name)
                        nodeGroup.links.new(input, newObjectNode.outputs[1])
                                               
                            
        context.scene.graphing = False
            
        return {'FINISHED'}



# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class SceneTree(NodeTree):
    '''Scene Nodes'''
    bl_idname = 'SceneTreeType'
    bl_label = 'Scene'
    bl_icon = 'SCENE_DATA'


# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class MyCustomTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SceneTreeType'


# Derived from the Node base type.
class SceneNode(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'SceneNodeType'
    bl_label = 'Scene'
    bl_icon = 'SCENE_DATA'

    sceneIndex = bpy.props.IntProperty()
    
    #newScene = bpy.props.BoolProperty(default=False)
#    otherIndex = len(bpy.data.scenes)

#    print(sceneIndex)
##        
#    if newScene:
#        
#        bpy.data.scenes.new("Scene")
#        
#        sceneIndex = len(bpy.data.scenes)-1


    # === Optional Functions ===
    # Initialization function, called when a new node is created.
    # This is the most common place to create the sockets for a node, as shown below.
    # NOTE: this is not the same as the standard __init__ function in Python, which is
    #       a purely internal Python method and unknown to the node system!
    def init(self, context):
        #self.inputs.new('CustomSocketType', "Hello")
        self.outputs.new('NodeSocketFloat', "Scene")
                   

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)
        
        bpy.data.scenes.new("Scene")
        self.sceneIndex = self.sceneIndex + 1

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")
        
        #Don't delete scene if node is deleted during graphing and scene isn't last scene
        if len(bpy.data.scenes) > 0 and not bpy.context.scene.graphing:
            
            bpy.data.scenes.remove(bpy.data.scenes[self.sceneIndex])

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):

        layout.prop(bpy.data.scenes[self.sceneIndex], "name", text="", icon="SCENE_DATA")

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
#    def draw_buttons_ext(self, context, layout):
#        layout.prop(self, "myFloatProperty")
#        # myStringProperty button will only be visible in the sidebar
#        layout.prop(self, "myStringProperty")

    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically
    def draw_label(self):
        return "Scene Node"



class ObjectNode(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'ObjectNodeType'
    bl_label = 'Object'
    bl_icon = 'OBJECT_DATA'

    objectIndex = bpy.props.IntProperty()
    scene = bpy.props.StringProperty(default=bpy.data.scenes[0].name)
    
    def init(self, context):
                
        self.inputs.new('NodeSocketFloat', "Parent")
        self.outputs.new('NodeSocketFloat', "Child")
        

    def update(self):
        
        #print("updating node: ", self.name, len(self.inputs[0].links))
        
        scene = bpy.data.scenes[self.scene]
        
        if len(self.inputs[0].links) != 1:
                        
            scene.objects[self.objectIndex].parent = None
                        
            nodeGroup = bpy.data.node_groups['NodeTree']
            
            nodeGroup.links.new(self.inputs[0], nodeGroup.nodes[scene.name].outputs[0])  
            
        else:
            
            parentName = self.inputs[0].links[0].from_node.name
                                    
            #print(parentName)
            
            if parentName != "Scene":
            
                scene.objects[self.objectIndex].parent = scene.objects[parentName]
        

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)
        
        scene = bpy.data.scenes[self.scene]
        
        object = scene.objects[self.objectIndex]
                        
        if object.type == "CAMERA":
            
            newCamera = bpy.data.cameras.new(object.name)
            
            newObject = bpy.data.objects.new(object.name, newCamera)
            
            scene.objects.link(newObject)
            scene.update()
            
            #Link new node with parent of original node
            nodeGroup = bpy.data.node_groups['NodeTree']
            oldParentNode = nodeGroup.nodes[object.name].inputs[0].links[0].from_node   
            nodeGroup.links.new(self.inputs[0], oldParentNode.outputs[0])
            
            reIndex(scene)            
            
    # Free function to clean up on removal.
    def free(self):
        
        scene = bpy.data.scenes[self.scene]
        
        if not scene.graphing:
             
            scene = bpy.data.scenes[self.scene]
            
            scene.objects[self.objectIndex].select = True
            bpy.ops.object.delete()
            
            reIndex(scene)
            
            print("Removing node ", self, ", Goodbye!")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        
        scene = bpy.data.scenes[self.scene]
        
        layout.prop(scene.objects[self.objectIndex], "name", text="", icon=scene.objects[self.objectIndex].type+"_DATA")

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
#    def draw_buttons_ext(self, context, layout):
#        layout.prop(self, "myFloatProperty")
#        # myStringProperty button will only be visible in the sidebar
#        layout.prop(self, "myStringProperty")

    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically
    def draw_label(self):
        return "Object Node"



def reIndex(scene):
    
    for objectIndex, object in enumerate(scene.objects):
                
        bpy.data.node_groups['NodeTree'].nodes[object.name].objectIndex = objectIndex



class MaterialNode(Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'MaterialNodeType'
    bl_label = 'Material'
    bl_icon = 'MATERIAL_DATA'

    materialIndex = bpy.props.IntProperty()


    def init(self, context):
                
        self.inputs.new('NodeSocketFloat', "Object")
        
        
#    def update(self):
#        
#        print("updating node: ", self.name, len(self.inputs[0].links))
                
    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        
        print("Copying from node ", node)
 
    # Free function to clean up on removal.
    def free(self):
        
        print("Removing node ", self, ", Goodbye!")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):

        layout.prop(bpy.data.materials[self.materialIndex], "name", text="", icon="MATERIAL_DATA")

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
#    def draw_buttons_ext(self, context, layout):
#        layout.prop(self, "myFloatProperty")
#        # myStringProperty button will only be visible in the sidebar
#        layout.prop(self, "myStringProperty")

    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically
    def draw_label(self):
        return "Material Node"




### Node Categories ###
# Node categories are a python system for automatically
# extending the Add menu, toolbar panels and search operator.
# For more examples see release/scripts/startup/nodeitems_builtins.py

# our own base class with an appropriate poll function,
# so the categories only show up in our own tree type
class MyNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'SceneTreeType'

# all categories in a list
node_categories = [
    # identifier, label, items list
    MyNodeCategory("SCENENODES", "Scene Nodes", items=[
        # our basic node
        NodeItem("SceneNodeType"),
        ]),
    MyNodeCategory("OBJECTNODES", "Object Nodes", items=[
        # the node item can have additional settings,
        # which are applied to new nodes
        # NB: settings values are stored as string expressions,
        # for this reason they should be converted to strings using repr()
        NodeItem("ObjectNodeType", label="Cube", settings={
            "scene": repr(bpy.context.scene.name)
            })
        ]),
    ]



def SceneNodesHeader(self, context):
    
    layout = self.layout
    
    row = layout.row()
    row.operator("scene_nodes.graph_scene", text="Graph Scene")



def register():

    bpy.utils.register_module(__name__)    

    bpy.types.NODE_HT_header.append(SceneNodesHeader)

    if 'SCENE_NODES' in nodeitems_utils._node_categories:
        nodeitems_utils.unregister_node_categories("SCENE_NODES")
    nodeitems_utils.register_node_categories("SCENE_NODES", node_categories)
    

def unregister():
    
    bpy.utils.unregister_module(__name__) 
    
    nodeitems_utils.unregister_node_categories("SCENE_NODES")


#if __name__ == "__main__":
#    register()
#    

register()    
