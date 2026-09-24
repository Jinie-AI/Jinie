import React from 'react';
import {View,Text,Pressable} from 'react-native';
export default function ProductCard({product,primary,dark,onOpen,onAdd,horizontal=false}) {
return <View style={{padding:16,borderRadius:18,backgroundColor:dark?'#211c2d':'#ffffff',flexDirection:horizontal?'row':'column'}}>
<Pressable accessibilityRole="button" accessibilityLabel={'View '+product.name} onPress={onOpen}><Text style={{fontSize:40}}>{product.icon}</Text><Text style={{color:dark?'#ffffff':'#221d32'}}>{product.name}</Text></Pressable>
<Text style={{color:primary}}>Rs. {product.price.toLocaleString()}</Text>
<Pressable accessibilityRole="button" accessibilityLabel={'Add '+product.name+' to bag'} onPress={onAdd}><Text style={{color:primary}}>Add to bag</Text></Pressable>
</View>;
}
