import React from 'react';
import {View,Text,Pressable,TextInput,StyleSheet} from 'react-native';
export default function NavigationTab({label='Home',active=false,onPress,primary='#7856d8'}) { return <Pressable accessibilityRole='tab' accessibilityState={{selected:active}} onPress={onPress} style={{padding:14,borderRadius:12,backgroundColor:active?primary+'20':'transparent'}}><Text style={{color:active?primary:'#8a7c98',fontWeight:'600'}}>{label}</Text></Pressable>; }
