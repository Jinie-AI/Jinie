import React from 'react';
import {View,Text,Pressable,TextInput,StyleSheet} from 'react-native';
export default function ContactCard({email='hello@example.com',phone='+92 300 0000000',address='Islamabad, Pakistan'}) { return <View style={{padding:22,borderRadius:20,backgroundColor:'#f4eefb',gap:12}}><Text style={{fontSize:23,fontWeight:'700'}}>Get in touch</Text><Text selectable>{email}</Text><Text selectable>{phone}</Text><Text>{address}</Text></View>; }
