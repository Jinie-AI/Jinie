import React from 'react';
import {View,Text,Pressable,TextInput,StyleSheet} from 'react-native';
export default function AboutCard({name='Our story',description='Thoughtful essentials, made for everyday life.'}) { return <View style={{padding:24,gap:16}}><Text style={{fontSize:28,fontWeight:'700'}}>{name}</Text><Text style={{fontSize:16,lineHeight:25,color:'#746580'}}>{description}</Text></View>; }
