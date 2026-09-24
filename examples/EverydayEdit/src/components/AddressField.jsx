import React from 'react';
import {View,Text,Pressable,TextInput,StyleSheet} from 'react-native';
export default function AddressField({value='',onChangeText,error=''}) { return <View><TextInput accessibilityLabel='Delivery address' value={value} onChangeText={onChangeText} placeholder='Delivery address' multiline style={{padding:14,borderWidth:1,borderColor:error?'#be6755':'#ddd4e8',borderRadius:12}}/>{error!==''&&<Text accessibilityRole='alert' style={{color:'#be6755',marginTop:5}}>{error}</Text>}</View>; }
