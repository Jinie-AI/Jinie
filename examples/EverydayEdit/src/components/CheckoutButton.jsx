import React from 'react';
import {View,Text,Pressable,TextInput,StyleSheet} from 'react-native';
export default function CheckoutButton({label='Continue to checkout',onPress,disabled=false,primary='#7856d8'}) { return <Pressable accessibilityRole='button' accessibilityState={{disabled}} disabled={disabled} onPress={onPress} style={{padding:16,borderRadius:14,backgroundColor:primary,opacity:disabled?.5:1}}><Text style={{textAlign:'center',color:'white',fontWeight:'700'}}>{label}</Text></Pressable>; }
