import React from 'react';
import {View,Text,Pressable,TextInput,StyleSheet} from 'react-native';
export default function CategoryChip({label='Essentials',selected=false,onPress,primary='#7856d8'}) { return <Pressable accessibilityRole='button' accessibilityState={{selected}} onPress={onPress} style={{padding:12,borderRadius:30,backgroundColor:selected?primary:'#eee9f5'}}><Text style={{color:selected?'white':'#483a60'}}>{label}</Text></Pressable>; }
