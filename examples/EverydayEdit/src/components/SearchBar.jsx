import React from 'react';
import {View,Text,Pressable,TextInput,StyleSheet} from 'react-native';
export default function SearchBar({value='',onChangeText,placeholder='Search products'}) { return <TextInput accessibilityLabel={placeholder} value={value} onChangeText={onChangeText} placeholder={placeholder} style={{padding:14,borderWidth:1,borderColor:'#ddd4e8',borderRadius:14,color:'#302338'}}/>; }
